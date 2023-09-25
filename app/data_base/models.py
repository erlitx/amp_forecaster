from .. import db
from flask import current_app, jsonify
from datetime import datetime
from sqlalchemy import desc, func


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    odoo_id = db.Column(db.Integer, unique=True, index=True)
    int_ref = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(128), unique=False, index=True)
    categ_name = db.Column(db.String(128), index=True)
    sale_ok = db.Column(db.Boolean, default=True)
    odoo_tmpl_id = db.Column(db.Integer, index=True)
    inventory = db.relationship('Inventory', back_populates='product')
    out_of_stock_inventory = db.relationship('Out_of_stock', back_populates='product')


    @staticmethod
    def add_product(odoo_id, int_ref, name, categ_name, sale_ok):
        #Check the name length
        if len(name) > 128:
            name = name[:126]
        product = Product(odoo_id=odoo_id, int_ref=int_ref, name=name, categ_name=categ_name, sale_ok=sale_ok)
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update_odoo_tmpl_id():
        id_list = Product.query.with_entities(Product.odoo_id).all()
        id_list = [record[0] for record in id_list]
        from ..api.odoo_api_request import get_odoo_tmp_id
        product_list = get_odoo_tmp_id(id_list)
        for product_item in product_list:
            product = Product.query.filter_by(odoo_id=product_item['odoo_id']).first()
            if product:
                product.odoo_tmpl_id = product_item['odoo_tmpl_id']
                db.session.commit()
        return True

    def to_dict(self):
        return {
            "int_ref": self.int_ref,
            "name": self.name,
            "inventory": [inventory_item.to_dict() for inventory_item in self.inventory]
        }

    def to_dict_simple(self):
        return {
            "int_ref": self.int_ref,
            "name": self.name
        }

    def __repr__(self):
        return '<Product {}>'.format(self.int_ref)

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(64), unique=True, index=True)
    inventory = db.relationship('Inventory', back_populates='warehouse')
    out_of_stock_inventory = db.relationship('Out_of_stock', back_populates='warehouse')

    @staticmethod
    def add_warehouse(location_name):
        warehouse = Warehouse(location_name=location_name)
        db.session.add(warehouse)
        db.session.commit()
        return warehouse

    def to_dict(self):
        return {
            "location_name": self.location_name
        }

    def __repr__(self):
        return '<Warehouse {}>'.format(self.location_name)

class Inventory(db.Model):
    __tablename__ = 'inventories'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    product = db.relationship('Product', back_populates='inventory')
    warehouse = db.relationship('Warehouse', back_populates='inventory')
    quantity = db.Column(db.Integer)
    quantity_reserved = db.Column(db.Integer)
    quantity_available = db.Column(db.Integer)
    inventory_date = db.Column(db.DateTime, default=datetime.utcnow)
    out_of_stock = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "warehouse_id": self.warehouse_id,
            "product_int_ref": self.product.int_ref,
            "product_name": self.product.name,
            "quantity": self.quantity,
            "warehouse_location_name": self.warehouse.location_name,
            "inventory_date": self.inventory_date
        }

    @staticmethod
    def add_inventory(product_id, warehouse_id, quantity, quantity_reserved,
                      quantity_available, out_of_stock, inventory_date):
        inventory = Inventory(product_id=product_id, warehouse_id=warehouse_id, inventory_date=inventory_date,
                              quantity=quantity, quantity_reserved=quantity_reserved,
                              quantity_available=quantity_available, out_of_stock=out_of_stock)
        db.session.add(inventory)
        db.session.commit()
        return inventory


# Return a json object with the latest inventory for a product in a location
    @staticmethod
    def get_inventory(int_ref, location_name):
        product = Product.query.filter_by(int_ref=int_ref).first()
        if product is None:
            return {'error': f'Product {int_ref} not found'}
        location = Warehouse.query.filter_by(location_name=location_name).first()
        if location is None:
            return {'error': f'Warehouse {location_name} not found'}
        inventory_locations = Inventory.query.filter_by(product_id=product.id, warehouse_id=location.id)
        latest_inventory = inventory_locations.order_by(desc(Inventory.inventory_date)).first()

        inventory = {'product_id': latest_inventory.product.id,
                     'product_int_ref': latest_inventory.product.int_ref,
                     'product_name': latest_inventory.product.name,
                     'quantity': latest_inventory.quantity,
                     'date': latest_inventory.inventory_date,
                     'location_name': latest_inventory.warehouse.location_name
                     }
        return inventory

    @staticmethod
    def get_inventory_by_locations(int_ref):
        product = Product.query.filter_by(int_ref=int_ref).first()
        if product is None:
            return {'error': f'Product {int_ref} not found'}
        subquery = (
            db.session.query(
                Inventory.warehouse_id,
                func.max(Inventory.inventory_date).label("max_date")
            )
            .filter_by(product_id=product.id)
            .group_by(Inventory.warehouse_id)
            .subquery()
        )

        latest_inventories = (
            db.session.query(Inventory)
            .join(subquery, (Inventory.warehouse_id == subquery.c.warehouse_id) & (Inventory.inventory_date == subquery.c.max_date))
            .all()
        )

        result = []
        for inventory in latest_inventories:
            result.append({
                'product_id': inventory.product.id,
                'product_int_ref': inventory.product.int_ref,
                'product_name': inventory.product.name,
                'quantity': inventory.quantity,
                'date': inventory.inventory_date,
                'location_name': inventory.warehouse.location_name
            })

        return result


    @staticmethod
    def current_stock_tableview():
        inventory = db.session.query(Inventory).order_by(desc(Inventory.inventory_date)).all()
        warehouse_list = [item.location_name for item in db.session.query(Warehouse).all()]
        product_list = [item.int_ref for item in db.session.query(Product).all()]
        inventory = []
        for warehouse in warehouse_list:
            for product in product_list:
                inventories = db.session.query(Inventory) \
                    .join(Product) \
                    .join(Warehouse) \
                    .filter(Product.int_ref == product) \
                    .filter(Warehouse.location_name == warehouse) \
                    .order_by(desc(Inventory.inventory_date)) \
                    .first()
                if inventories is not None:
                    inventory.append(inventories.to_dict())
        return inventory

    @staticmethod
    def current_stock_nested():
        inventory = []
        for i, product in enumerate(db.session.query(Product).all()):
            inventory.append({
                'product_id': product.id,
                'product_int_ref': product.int_ref,
                'product_name': product.name,
            })
            for warehouse in db.session.query(Warehouse).all():
                inventories = db.session.query(Inventory) \
                                        .join(Product) \
                                        .join(Warehouse) \
                                        .filter(Product.int_ref == product.int_ref) \
                                        .filter(Warehouse.location_name == warehouse.location_name) \
                                        .order_by(desc(Inventory.inventory_date)) \
                                        .first()
                # Check if there is an inventory for this product in this warehouse
                # If there is, add it to the inventory list
                if inventories is not None:
                    inventory[i][warehouse.location_name] = [inventories.quantity, inventories.inventory_date]
        print(inventory[0])
        return inventory


    # Method makes API request to Odoo and updates the Inventory table in the db
    # If products or warehouses do not exist in the db, they will be added through the add_product() and add_warehouse methods()
    @staticmethod
    def update_inventory_from_odoo(product_num=1):
        # Get API request to Odoo
        from ..api.odoo_api_request import odoo_api_get_inventory
        odoo_inventory = odoo_api_get_inventory(product_num)
        products = []
        datetime_of_request = datetime.utcnow()

        # Iterate over products in 1st level of dict and add them to db if they don't exist
        for product in odoo_inventory.items():
            int_ref = product[1].get('default_code')
            odoo_id = product[1].get('id')
            categ_name = product[1].get('categ_id')[1]
            name = product[1].get('name')
            sale_ok = product[1].get('sale_ok')
            print(f'========\n{int_ref}\n{odoo_id}\n{categ_name}\n{name}\n{sale_ok}\n========')

            #Check if product category in a list of categories that we want to get
            if categ_name not in ['All / Saleable']:
                continue

            # Check if product exists in db, if not add it
            product_check = db.session.query(Product).filter_by(int_ref=int_ref).first()
            if product_check is None:
                Product.add_product(odoo_id, int_ref, name, categ_name, sale_ok)

            prod_id = db.session.query(Product).filter_by(int_ref=int_ref).first().id

            # Iterate over locations in 2nd level of nested  dict and add them to db if they don't exist
            for location in product[1].get('qty_available_at_location').values():
                location_name = location.get('display_name')
                if db.session.query(Warehouse).filter_by(location_name=location_name).first() is None:
                    Warehouse.add_warehouse(location_name)
                warehouse_id = db.session.query(Warehouse).filter_by(location_name=location_name).first().id
                quantity = location.get('qty_available')
                quantity_reserved = location.get('qty_reserved')
                quantity_available = quantity - quantity_reserved
                # Dict for view purposes
                inventory_view = {'product_id': prod_id,
                                  'warehouse_id': warehouse_id,
                                  'odoo_id': odoo_id,
                                  'int_ref': int_ref,
                                  'name': name, 'categ_name': categ_name,
                                  'location_name': location_name,
                                  'quantity': quantity,
                                  'quantity_available': quantity_available,
                                  'quantity_reserved': quantity_reserved,
                                  'out_of_stock': quantity_available <= 0,
                                  'sale_ok': sale_ok}
                products.append(inventory_view)

                #Dict to pass values to Inventory.add_inventory method
                inventory = {'product_id': prod_id,
                             'warehouse_id': warehouse_id,
                             'quantity': quantity,
                             'quantity_available': quantity_available,
                             'quantity_reserved': quantity_reserved,
                             'out_of_stock': quantity_available <= 0,
                             'inventory_date': datetime_of_request
                             }
                # Unpack inventory dict and add to db as individual args
                Inventory.add_inventory(**inventory)

                # Unpack inventory dict and add to db only if out of stock = True
                # if quantity_available <= 0:
                #     Out_of_stock.add_out_of_stock(**inventory)

        return products


    def __repr__(self):
        return '<Inventory: prod: {} qty: {} at {} on {}>'.format(self.product.int_ref, self.quantity,
                                                            self.warehouse.location_name, self.inventory_date)


class Out_of_stock(db.Model):
    __tablename__ = 'out_of_stock_products'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    quantity_reserved = db.Column(db.Integer)
    quantity_available = db.Column(db.Integer)
    inventory_date = db.Column(db.DateTime, default=datetime.utcnow)
    out_of_stock = db.Column(db.Boolean, default=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    product = db.relationship('Product', back_populates='out_of_stock_inventory')
    warehouse = db.relationship('Warehouse', back_populates='out_of_stock_inventory')

    # Method makes API request to Odoo and updates the Inventory table in the db
    # If products or warehouses do not exist in the db, they will be added through the add_product() and add_warehouse methods()
    @staticmethod
    def update_inventory_from_odoo(product_num=1):
        # Get API request to Odoo
        from ..api.odoo_api_request import odoo_api_get_inventory
        odoo_inventory = odoo_api_get_inventory(product_num)
        products = []
        datetime_of_request = datetime.utcnow()

        # Iterate over products in 1st level of dict and add them to db if they don't exist
        for product in odoo_inventory.items():
            int_ref = product[1].get('default_code')
            odoo_id = product[1].get('id')
            categ_name = product[1].get('categ_id')[1]
            name = product[1].get('name')
            sale_ok = product[1].get('sale_ok')


            # Check if product category in a list of categories that we want to get
            if categ_name not in ['All / Saleable']:
                continue #if not in list, skip to next item in a dict

            print(f'========\n{int_ref}\n{odoo_id}\n{categ_name}\n{name}\n{sale_ok}\n========')

            # Check if product exists in db, if not add it
            product_check = db.session.query(Product).filter_by(int_ref=int_ref).first()
            if product_check is None:
                Product.add_product(odoo_id, int_ref, name, categ_name, sale_ok)
                product_check = db.session.query(Product).filter_by(int_ref=int_ref).first()
            # Check if product name in db is the same as in Odoo, if not update it
            elif product_check.name != name:
                product_check.name = name
                db.session.commit()
            elif product_check.categ_name != categ_name:
                product_check.categ_name = categ_name
                db.session.commit()

            # Get product id from db (now it's definitely exist because of previous check and creation)
            prod_id = db.session.query(Product).filter_by(int_ref=int_ref).first().id

            # Check dict if product is in stock at AMPRU, make calculations to get quantity_available
            ampru_location_check = product[1].get('qty_available_at_location')[141]     #get AMPRU location from dict
            quantity = ampru_location_check.get('qty_available')
            quantity_reserved = ampru_location_check.get('qty_reserved')
            quantity_available = quantity - quantity_reserved
            print(f'---\n{ampru_location_check}\n---')
            print(f'-\t{quantity}\t{quantity_reserved}\t{quantity_available}-')

            # If product is out of stock at AMPRU, do other stuff to get all locations qtys and write the results to db
            # If product is in stock at AMPRU, skip to next product in a dict
            if quantity_available <= 0:

                # Iterate over locations in 2nd level of nested  dict and add warehouse to db if they don't exist
                for location in product[1].get('qty_available_at_location').values():
                    location_name = location.get('display_name')

                    # Check if warehouse exists in db, if not add it
                    if db.session.query(Warehouse).filter_by(location_name=location_name).first() is None:
                        Warehouse.add_warehouse(location_name)

                    # Get warehouse id from db (now it's definitely exist because of previous check and creation)
                    warehouse_id = db.session.query(Warehouse).filter_by(location_name=location_name).first().id
                    quantity = location.get('qty_available')
                    quantity_reserved = location.get('qty_reserved')
                    quantity_available = quantity - quantity_reserved
                    # Dict for view purposes
                    inventory_view = {'product_id': prod_id,
                                      'warehouse_id': warehouse_id,
                                      'odoo_id': odoo_id,
                                      'int_ref': int_ref,
                                      'name': name, 'categ_name': categ_name,
                                      'location_name': location_name,
                                      'quantity': quantity,
                                      'quantity_available': quantity_available,
                                      'quantity_reserved': quantity_reserved,
                                      'out_of_stock': quantity_available <= 0,
                                      'sale_ok': sale_ok,
                                      'inventory_date': datetime_of_request
                                      }
                    products.append(inventory_view)

                    # Dict to pass values to Inventory.add_inventory method
                    inventory = {'product_id': prod_id,
                                 'warehouse_id': warehouse_id,
                                 'quantity': quantity,
                                 'quantity_available': quantity_available,
                                 'quantity_reserved': quantity_reserved,
                                 'out_of_stock': quantity_available <= 0,
                                 'inventory_date': datetime_of_request
                                 }

                    # Unpack inventory dict and add to db only if out of stock = True
                    Out_of_stock.add_inventory(**inventory)

        return products

    @staticmethod
    def add_inventory(product_id, warehouse_id, quantity, quantity_reserved,
                      quantity_available, out_of_stock, inventory_date):
        inventory = Out_of_stock(product_id=product_id, warehouse_id=warehouse_id, inventory_date=inventory_date,
                              quantity=quantity, quantity_reserved=quantity_reserved,
                              quantity_available=quantity_available, out_of_stock=out_of_stock)
        db.session.add(inventory)
        db.session.commit()
        return inventory

    # Return a nested dict with all {products: {and their locations]} from Out_of_stock table
    @staticmethod
    def current_stock_nested():
        # Get the latest inventory_date from Out_of_stock inventory_date column
        latest_inventory_date = db.session.query(func.max(Out_of_stock.inventory_date)).scalar_subquery()

        # Get all unique product_id from Out_of_stock product_id column filtered also by latest date (result is a list of tuples)
        products = db.session.query(Out_of_stock.product_id)\
                             .filter(Out_of_stock.inventory_date == latest_inventory_date)\
                             .distinct().all()

        # Get all unique warehouses_id from Out_of_stock warehouse_id column (result is a list of tuples)
        warehouses = db.session.query(Out_of_stock.warehouse_id).distinct().all()
        # Put all warehouses_id in a list
        warehouse_list = [warehouse.warehouse_id for warehouse in warehouses]

        # Put all product_id in a list
        product_list = [product.product_id for product in products]
        print(product_list)


        #Get the latest inventories for each warehouse and product
        inventories = db.session.query(Out_of_stock)\
                                .join(Product)\
                                .join(Warehouse) \
                                .filter(Out_of_stock.inventory_date == latest_inventory_date) \
                                .all()
        #Test subquery
        # subquery = db.session.query(Out_of_stock)\
        #                         .join(Product)\
        #                         .join(Warehouse) \
        #                         .filter(Out_of_stock.inventory_date == latest_inventory_date) \
        #                         .subquery()

        inventory_list = []

        for i, product in enumerate(product_list):
            subquery = db.session.query(Product).filter(Product.id == product).first()

            # Get the first latest inventory about product and any warehouse put in a list
            subquery2 = db.session.query(Out_of_stock) \
                .join(Product) \
                .join(Warehouse) \
                .filter(Out_of_stock.inventory_date == latest_inventory_date, Out_of_stock.product_id == product) \
                .first()
            inventory_list.append({'product_odoo_id': subquery.odoo_id,
                                   'product_odoo_tmpl_id': subquery.odoo_tmpl_id,
                                   'product_int_ref': subquery.int_ref,
                                   'product_name': subquery.name,
                                   'date': subquery2.inventory_date})

            # Get all latest inventories about product and all warehouse put in a list
            subquery2 = db.session.query(Out_of_stock) \
                .join(Product) \
                .join(Warehouse) \
                .filter(Out_of_stock.inventory_date == latest_inventory_date, Out_of_stock.product_id == product) \
                .all()

            for item in subquery2:
                inventory_list[i][item.warehouse.location_name] = [item.quantity, item.quantity_available, item.quantity_reserved]

        # Get the latest inventory_date from Out_of_stock inventory_date column
        inventory_date = db.session.query(func.max(Out_of_stock.inventory_date)).scalar()

        # Return a list of dictionaries with a dict of latest inventories and one value of the latest inventory_date
        return [inventory_list, inventory_date]



class ProductsSaleable(db.Model):
    __tablename__ = 'products_saleable'
    id = db.Column(db.Integer, primary_key=True)
    odoo_id = db.Column(db.Integer)
    int_ref = db.Column(db.String(64))
    product_name = db.Column(db.String(128))
    quantity = db.Column(db.Integer)
    quantity_reserved = db.Column(db.Integer)
    quantity_available = db.Column(db.Integer)
    inventory_date = db.Column(db.DateTime, default=datetime.utcnow)
    out_of_stock = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "product_id": self.odoo_id,
            "int_ref": self.int_ref,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "quantity_available": self.quantity_available,
            "quantity_reserved": self.quantity_reserved,
            "warehouse_location_name": self.warehouse.location_name,
            "inventory_date": self.inventory_date
        }

    # Adds products to the db 'products_saleable' from Odoo API with args filter:
    # categ_id: default = 2 (All / Saleable)
    # num: default = 1 (number of products to get, 0 = all)
    def get_saleable_products(self, num=1, categ_id=2):
        from ..api.odoo_api_request import odoo_api_get_products, odoo_api_get_products_quants
        try:
            # get the list of products from Odoo with category = 2 (All / Saleable)
            saleable_products = odoo_api_get_products(num, categ_id)

            # get the product quants from Odoo
            
            datetime_of_request = datetime.utcnow()
            product_list_ids = []
            product_dict_ids = {}
            quants_dict = {}
            saleable_prod_list= []
            for product in saleable_products:
                print(f'---{product}')
                if len(product.get('name')) > 128:
                    product_name = product.get('name')[:126]
                else:
                    product_name = product.get('name')

                product_list_ids.append(product.get('id'))
                product_dict_ids[product.get('id')] = {'int_ref': product.get('default_code'),
                                                       'name': product_name}
            print(f'====={product_dict_ids}')

            quants = odoo_api_get_products_quants(prod_list_ids=product_list_ids)

            print(f'===+++=={quants}')

            for data in quants:
                product_id = data["product_id"][0]
                location_id = data["location_id"][0]
                # update quantity of product at location
                qty_available = data["quantity"]
                qty_reserved = data["reserved_quantity"]
                #print(f'---{product_id}---{location_id}---{qty_available}---{qty_reserved}')
                quants_dict[product_id] = {'location_id': location_id, 'qty_available': qty_available, 'qty_reserved': qty_reserved}

                # saleable_prod = ProductsSaleable(odoo_id=product_id, int_ref=product_dict_ids.get(product_id).get('int_ref'),
                                                #  product_name=product_dict_ids.get(product_id).get('name'), inventory_date=datetime_of_request,)

            print(f'///====={quants_dict}')

            #Compose final dict of quants based on product dict
            for product_id, product_value in product_dict_ids.items():
                
                odoo_id = product_id
                int_ref = product_value.get('int_ref')
                product_name = product_value.get('name')
                quantity=quants_dict.get(odoo_id, {}).get('qty_available')
                if quantity is None:
                    print("None--------")
                    quantity = 0
                    quantity_reserved = 0
                    quantity_available = 0
                else:
                    quantity_reserved=quants_dict.get(odoo_id).get('qty_reserved')
                    quantity_available=quantity-quantity_reserved
                print(f'@@@---{odoo_id}---{int_ref}---{product_name}---{quantity}---{quantity_reserved}---{quantity_available}')

                saleable_prod = ProductsSaleable(odoo_id=product_id, int_ref=product_value.get('int_ref'),
                                                     product_name=product_value.get('name'),
                                                     quantity=quantity, quantity_reserved=quantity_reserved,
                                                     quantity_available=quantity_available, inventory_date=datetime_of_request)

                db.session.add(saleable_prod)
                db.session.commit()                
            return product_list_ids
        
        except Exception as e:
            print(e)
            return False
        







# specific_product_id = 1  # Replace with the desired product_id
#
# # Subquery with the first filter condition (latest_inventory_date)
# subquery = (
#     db.session.query(Out_of_stock)
#     .join(Product)
#     .join(Warehouse)
#     .filter(Out_of_stock.inventory_date == latest_inventory_date)
#     .subquery()
# )
#
# # Main query using the subquery and applying the second filter condition (specific_product_id)
# inventories = (
#     db.session.query(subquery)
#     .filter(subquery.c.product_id == specific_product_id)
#     .all()
# )