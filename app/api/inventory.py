from flask import Response, json, jsonify, request, redirect, url_for
from . import api
from ..data_base.models import Product, Warehouse, Inventory, Out_of_stock
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from sqlalchemy import desc, func
from .odoo_api_request import odoo_api_get_inventory


@api.route('/add_product/<string:int_ref>/<string:name>')
def add_product(int_ref, name):
    product = Product.add_product(int_ref=int_ref, name=name)
    product_dict = product.to_dict()
    return jsonify(product_dict)

@api.route('/update_out_of_stock_from_odoo')
def update_out_of_stock_from_odoo():

    return jsonify(Out_of_stock.update_inventory_from_odoo(0))

# Update Out_of_stock table from Odoo, return to out_of_stock page
@api.route('/update_out_of_stock_from_odoo_nested', methods=['GET', 'POST'])
def update_out_of_stock_from_odoo_nested():
    Out_of_stock.update_inventory_from_odoo(0)
    return redirect(url_for('main.out_of_stock'))

@api.route('/update_odoo_tmpl')
def update_odoo_tmpl():
    result = Product.update_odoo_tmpl_id()
    return 'ok'


@api.route('/nested_list_out_of_stock')
def nested_list_out_of_stock():
    return jsonify(Out_of_stock.current_stock_nested())
###################

@api.route('/add_inventory/<string:int_ref>/<int:quantity>/<path:location_name>')
def add_inventory(int_ref, quantity, location_name):
    product = Product.query.filter_by(int_ref=int_ref).first()
    warehouse = Warehouse.query.filter_by(location_name=location_name).first()
    if not product:
        add_product(int_ref=int_ref, name='Just created')
        product = Product.query.filter_by(int_ref=int_ref).first()
    if not warehouse:
        add_warehouse(location_name=location_name)
        warehouse = Warehouse.query.filter_by(location_name=location_name).first()
    inventory = Inventory.add_inventory(product_id=product.id, warehouse_id=warehouse.id, quantity=quantity)
    inventory_dict = inventory.to_dict()
    return jsonify(inventory_dict)


@api.route('/add_warehouse/<path:location_name>')
def add_warehouse(location_name):
    warehouse = Warehouse.add_warehouse(location_name=location_name)
    warehouse_dict = warehouse.to_dict()
    return jsonify(warehouse_dict)


@api.route('/get_inventory')
def get_inventory_all():
    inventory = Inventory.query.all()
    inventory_list = [inventory.to_dict() for inventory in inventory]
    return jsonify(inventory_list)

@api.route('/get_inventory_all/<string:int_ref>/<path:location_name>')
def get_inventory_last(int_ref, location_name):
    return jsonify(Inventory.get_inventory(int_ref=int_ref, location_name=location_name))


@api.route('/get_last_stock/<string:int_ref>')
def get_inventory_by_location(int_ref):

    return jsonify(Inventory.get_inventory_by_locations(int_ref=int_ref))


@api.route('/get_product/<string:int_ref>')
def get_product(int_ref):
    product = Product.query.filter_by(int_ref=int_ref).first()
    if not product:
        return "Error: product not found", 404
    product = product.to_dict()
    return jsonify(product)


@api.route('/get_products')
def get_products():
    products = Product.query.all()
    products_list = [[product.int_ref, product.name] for product in products]
    return jsonify(products_list)

@api.route('/warehouse')
def get_warehouses():
    warehouse = Warehouse(location_name='PS/Prepair')
    db.session.add(warehouse)
    db.session.commit()
    warehouses = Warehouse.query.all()
    warehouses_list = [warehouse.to_dict() for warehouse in warehouses]
    return jsonify(warehouses_list)


# Test func to get all inventory by product using Inventory model instead of Product model
@api.route('/get_product_by_inv/<string:int_ref>')
def get_product_by_inv(int_ref):
    product = Product.query.filter_by(int_ref=int_ref).first()
    if not product:
        return "Error: product not found", 404
    inventory_list = Inventory.query.filter_by(product_id=product.id).all()
    inventory = [inventory.to_dict() for inventory in inventory_list]
    return jsonify(inventory)

@api.route('/get_inventory_by_product/<string:int_ref>')
def get_inventory_by_product(int_ref):
    product = Product.query.filter_by(int_ref=int_ref).first()
    if not product:
        return "Error: product not found", 404
    inventory = product.to_dict()
    return jsonify(inventory)


@api.route('/current_inventory')
def current_inventory():
    inventory = Inventory.current_stock()
    return jsonify(inventory)

# Testing
@api.route('/current_inventory2')
def current_inventory2():
    inventory = Inventory.current_stock_nested()
    return jsonify(inventory)

# Testing
# @api.route('/test_query/<string:int_ref>')
# def test_query(int_ref):
#     # inventory = (db.session.query(Inventory).join(Product).filter(Product.int_ref == int_ref).first())
#     # inventory = db.session.query(Inventory).filter(Inventory.inventory_date >= '2023-03-22 09:00:00').all()
#     inventory = db.session.query(Inventory).order_by(desc(Inventory.inventory_date)).all()
#     # inventory = db.session.query(Inventory).order_by(desc(Inventory.inventory_date)).limit(1).all()
#     # inventory = db.session.query(Inventory).order_by(desc(Inventory.inventory_date)).first()
#     warehouse_list = [item.location_name for item in db.session.query(Warehouse).all()]
#     product_list = [item.int_ref for item in db.session.query(Product).all()]
#     print(warehouse_list)
#     print(product_list)
#     inventory = []
#     for warehouse in warehouse_list:
#         for product in product_list:
#             inventories = db.session.query(Inventory)\
#                         .join(Product)\
#                         .join(Warehouse)\
#                         .filter(Product.int_ref == product)\
#                         .filter(Warehouse.location_name == warehouse)\
#                         .order_by(desc(Inventory.inventory_date))\
#                         .first()
#             if inventories is not None:
#                 inventory.append(inventories.to_dict())
#     return jsonify(inventory)
