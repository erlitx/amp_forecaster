from flask import render_template, flash, redirect, url_for, request
from . import auth
from .forms import LoginForm
from ..models import User, Role
from ..email import send_email
from .forms import RoleForm, UserForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from flask_login import login_user, logout_user, login_required, current_user
from ..api.authentication import auth_api

# This route takes two arguments, token and user_id (passed as **kwargs in the send_email func as user=user and token=token)
# In email html user=user is passed and there is a link generarted user_id=user.id and token=token is passed as token=token
# In the route we get the token and user_id, from user_id we get the user object and check if user.confirmed is True
# So we can check if user has already confirmed his email address without @login_required decorator and asking him to login
@auth.route('/confirm/<token>/<user_id>')
def confirm_noauth(token, user_id):
    user = User.query.get(user_id)
    # Check if user confirmed column data is TRUE
    if user.confirmed:
        return redirect(url_for('main.index'))
    # Call user.confirm method from models.py with argument token and check if it returns TRUE
    if user.confirm(token):
        # Write to database user.confirmed TRUE.
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
        return render_template('auth/confirmed.html')
    else:
        return 'The confirmation link is invalid or has expired.'


@auth.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    if current_user.role.name == "Admin":
        name = None
        form = UserForm()
        user_to_delete = User.query.get_or_404(id)
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('User deleted successfully')
            return redirect(url_for('auth.register_user'))
        except:
            flash('Something went wrong')
            return redirect(url_for('auth.register_user'))
    else:
        flash("You can't delete another User")
        return redirect(url_for('auth.register_user'))

@auth.route('/' , methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            if user.confirmed:
                login_user(user, form.remember_me.data)
                current_user.ping()
                db.session.commit()
                next = request.args.get('next')
                if next is None or not next.startswith('/'):
                    next = url_for('main.index')
                return redirect(next)
            return redirect(url_for('auth.unconfirmed'))

    return render_template('auth/login.html', form=form)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register_role', methods=['GET', 'POST'])
def register_role():
    roles = Role.query.order_by(Role.id).all()
    form_role = RoleForm()

    if form_role.validate_on_submit():
        role = Role(name=form_role.name.data)
        db.session.add(role)
        db.session.commit()

        flash('User Added')
    #role = Role(name='Admin')
    return render_template('auth/register_role.html', form_role=form_role, roles=roles)


@auth.route('/register_user', methods=['GET', 'POST'])
def register_user():
    users = User.query.order_by(User.id).all()
    form_user = RegistrationForm()
    if form_user.validate_on_submit():
        user = User.query.filter_by(email=form_user.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form_user.password.data, 'sha256')
            user = User(username=form_user.username.data, email=form_user.email.data,
                        password_hash=hashed_pw, role_id=form_user.role.data)
            db.session.add(user)
            db.session.commit()

            # Generate a confirmation token with user.generate_confirmation_token() method from models.py
            token = user.generate_confirmation_token()
            send_email(user.email, 'Confirm Your Account',
                       'auth/email/confirm', user=user, token=token)
            flash(f'A confirmation email has been sent to {user.email}')
            return redirect(url_for('auth.login'))

            flash(f'User {user.email} added')
            return redirect(url_for('auth.register_user'))

    #role = Role(name='Admin')
    return render_template('auth/register_user.html', form_user=form_user, users=users)


@auth.route('/reconfirm', methods=['GET', 'POST'])
def reconfirm():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            token = user.generate_confirmation_token()
            send_email(user.email, 'Confirm Your Account',
               'auth/email/confirm', user=user, token=token)
            flash('A new confirmation email has been sent to you by email.')

    return render_template('auth/reconfirm.html', form=form)


#This is route to confirm email address but onlu after user has logged in because we need current_user object
# @auth.route('/confirm/<token>')
# @login_required
# def confirm(token):
#     # Check if user confirmed column data is TRUE
#     if current_user.confirmed:
#         return redirect(url_for('main.index'))
#     # Call user.confirm method from models.py with argument token and check if it returns TRUE
#     if current_user.confirm(token):
#         # Write to database user.confirmed TRUE.
#         db.session.commit()
#         flash('You have confirmed your account. Thanks!')
#     else:
#         flash('The confirmation link is invalid or has expired.')
#     return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    # if current_user.is_anonymous or current_user.confirmed:
    #     return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')





