import json

from flask import render_template, current_app, session, flash, redirect, url_for, request, jsonify
# Import the Blueprint object from main/__init__.py
from . import main, errors
from ..models import User
from ..data_base.models import Product, Warehouse, Inventory, Out_of_stock
from .. import db
from ..auth.forms import UserForm, AboutForm, OutOfStock
from flask_login import login_required, current_user

#main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')

# @main.route('/out_of_stock', methods=['GET', 'POST'])
# @login_required
# def out_of_stock():
#     inventory_list = Inventory.get_inventory(int_ref='AMP-001', location_name='AMPRU/Stock')
#     json_list = jsonify(inventory_list)
#     json_list_data = json_list.get_data(as_text=True)
#     return render_template('out_of_stock.html', inventory_list=json_list_data, table_list=inventory_list)

@main.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = UserForm()
    form_about = AboutForm()
    user = User.query.filter_by(username=username).first_or_404()
    if request.method == 'POST':
        user.username = request.form['username']
        user.location = request.form['location']
        db.session.add(user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.user', username=user.username))
    return render_template('user.html', user=user, form=form, form_about=form_about)


@main.route('/current_inventory', methods=['GET', 'POST'])
def out_of_stock():
    form = OutOfStock()
    inventory = Out_of_stock.current_stock_nested()[0]
    date = Out_of_stock.current_stock_nested()[1]
    inventory_time = db.session.query(Out_of_stock).order_by(Out_of_stock.id.desc()).first()
    return render_template('out_of_stock.html', inventory=inventory, date=date, form=form)

