import json
from flask import render_template, current_app, session, flash, redirect, url_for, request, jsonify
# Import the Blueprint object from main/__init__.py
from . import main, errors
from ..models import User, Role
from ..data_base.models import Product, Warehouse, Inventory, Out_of_stock
from .. import db
from ..auth.forms import UserForm, AboutForm, OutOfStock
from flask_login import login_required, current_user
from datetime import datetime
import pytz

@main.route('/main')
def index():
    return redirect(url_for('main.out_of_stock'))

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


@main.route('/', methods=['GET', 'POST'])
@login_required
def out_of_stock():
    form = OutOfStock()
    #Get nestet dict of all out_of_stock products
    inventory = Out_of_stock.current_stock_nested()[0]
    #Get date from last update from nested dict
    date = Out_of_stock.current_stock_nested()[1]
    return render_template('out_of_stock.html', inventory=inventory, date=date, form=form)

@main.route('/admin_panel', methods=['GET', 'POST'])
@login_required
def admin_panel():

    return render_template('admin_panel.html', users=User.query.all(), roles=Role.query.all())

