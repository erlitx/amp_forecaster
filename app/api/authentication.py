from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User
from . import api


auth_api = HTTPBasicAuth()

# Connect this function with HTTPBasicAuth as an authentication function (used only once)
@auth_api.verify_password
def verify_password(username, password):
    # Here, you should verify the provided username and password against your user database.
    # For demonstration purposes, we are using a simple check.
    if username == 'user' and password == '1234':
        return True
    return False


# This route function requires authentication
@api.route('/secure')
@auth_api.login_required
def secure_route():
    return jsonify({"message": "This is a secure route."})


# @auth.verify_password
# def verify_password(email_or_token, password):
#     if email_or_token == '':
#         return False
#     if password == '':
#         g.current_user = User.verify_auth_token(email_or_token)
#         g.token_used = True
#         return g.current_user is not None
#     user = User.query.filter_by(email=email_or_token.lower()).first()
#     if not user:
#         return False
#     g.current_user = user
#     g.token_used = False
#     return user.verify_password(password)
#
#
# @auth.error_handler
# def auth_error():
#     return unauthorized('Invalid credentials')