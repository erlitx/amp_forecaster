from flask import Response, json, jsonify, request, redirect, url_for
from . import api
from ..data_base.models import ProductsSaleable
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from sqlalchemy import desc, func
from .authentication import auth_api
from flask_login import login_required, current_user
from datetime import datetime
from .odoo_api_request import odoo_api_get_products_quants




@api.route('/test_stock')
@login_required
def test_stock():
    #result = Out_of_stock.update_inventory_from_odoo(0)
    odoo = ProductsSaleable()
    odoo_products = odoo.get_saleable_products(num=5, categ_id=2)

    odoo_quants = odoo_api_get_products_quants(prod_list_ids=odoo_products)
    #print(odoo_quants)


    return jsonify(odoo_products)



