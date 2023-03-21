from flask import Response, json, jsonify, request, redirect, url_for
from . import api
from ..models import User, Role
from werkzeug.security import generate_password_hash, check_password_hash


@api.route('/users')
def get_users():
    users = User.query.all()
    user_list = [user.to_json() for user in users]
    return jsonify(user_list)


# Test route which returns a user only if user password is provided in URL
@api.route('/users/<string:username>/<string:password>')
def get_user_secure(username, password):
    user = User.query.filter_by(username=username).first()
    is_password_correct = check_password_hash(user.password_hash, password)
    if is_password_correct:
        user = User.query.filter_by(username=username).first().to_json()
        return jsonify(user)
    else:
        return 'Bad password'

@api.route('/user_create/')
def user_create():
    username = request.args.get('username')
    email = request.args.get('email')
    password = request.args.get('password')
    role_id = request.args.get('role_id')
    password_hash = generate_password_hash(password, 'sha256')
    role = Role.query.filter_by(name=role_id).first()
    if role is None:
        return 'Role not found', 400
    user = User.create_user(username, email, password_hash, role.id)
    return 'User created', 201
