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

            # Get product id from db (now it's definitely exist because of previous check and creation)
            prod_id = db.session.query(Product).filter_by(int_ref=int_ref).first().id

            # Check dict if product in stock at AMPRU, make calculations to get quantity_available
            ampru_location_check = product[1].get('qty_available_at_location')[141]     #get AMPRU location from dict
            quantity = ampru_location_check.get('qty_available')
            quantity_reserved = ampru_location_check.get('qty_reserved')
            quantity_available = quantity - quantity_reserved
            print(f'---\n{ampru_location_check}\n---')
            print(f'-\t{quantity}\t{quantity_reserved}\t{quantity_available}-')

            # If product is out of stock at AMPRU, do other stuff to get all locations qtys and write the results to db
            # If product is in stock at AMPRU, skip to next product in a dict
            if quantity_available <= 0:

                # Iterate over locations in 2nd level of nested  dict and add them to db if they don't exist
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
                                      'sale_ok': sale_ok}
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


