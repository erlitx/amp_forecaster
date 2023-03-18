from flask import render_template, current_app, session, flash, redirect, url_for, request
# Import the Blueprint object from main/__init__.py
from . import main, errors
from ..models import User
from .. import db
from ..auth.forms import UserForm, AboutForm
from flask_login import login_required, current_user

#main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/user/<username>', methods=['GET', 'POST'])
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

