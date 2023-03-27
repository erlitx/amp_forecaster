from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, Email, equal_to, Regexp, EqualTo
from ..models import User, Role


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class AboutForm(FlaskForm):
    location = StringField('Location')


class RoleForm(FlaskForm):
    name = StringField('Role Name', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('Register')

class UserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password_repeat', message='Passwords Must Match!')])
    password_repeat = PasswordField('Repeat Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('1', 'Admin'), ('0', 'User')])
    submit = SubmitField('Register')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('Password', validators=[DataRequired(), equal_to('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('1', 'Admin'), ('3', 'User')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class OutOfStock(FlaskForm):
    submit = SubmitField('Refresh')
