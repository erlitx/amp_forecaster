from flask import Response, json, jsonify
from . import api
from ..models import User
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
