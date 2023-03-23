from .. import db
from flask import current_app, jsonify
from datetime import datetime
from sqlalchemy import desc, func

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    int_ref = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64), unique=False, index=True)
    inventory = db.relationship('Inventory', back_populates='product')

    @staticmethod
    def add_product(int_ref, name):
        product = Product(int_ref=int_ref, name=name)
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
    inventory_date = db.Column(db.DateTime, default=datetime.utcnow)

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
    def add_inventory(product_id, warehouse_id, quantity):
        inventory = Inventory(product_id=product_id, warehouse_id=warehouse_id, quantity=quantity)
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
                if inventories is not None:
                    inventory[i][warehouse.location_name] = [inventories.quantity, inventories.inventory_date]
        print(inventory[0])
        return inventory
    # Inventory return format:
    # {'product_id': 1, 'product_int_ref': 'AMP-001', 'product_name': 'Motor Shield',
    #  'AMPRU/Stock': [68, datetime.datetime(2023, 3, 23, 8, 24, 36, 85175)],
    #  'PS/Prepair': [50, datetime.datetime(2023, 3, 22, 7, 31, 52, 937128)]}


    def __repr__(self):
        return '<Inventory: prod: {} qty: {} at {} on {}>'.format(self.product.int_ref, self.quantity,
                                                            self.warehouse.location_name, self.inventory_date)

