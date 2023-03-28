from flask import g, jsonify, session
from flask_httpauth import HTTPBasicAuth
from ..models import User
from . import api
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

auth_api = HTTPBasicAuth()

# Connect this function with HTTPBasicAuth as an authentication function (used only once)
@auth_api.verify_password
def verify_password(username, password):
    # Here, you should verify the provided username and password against your user database.
    # Ask browser to requery username and password. Withput this line, the browser will not ask for username and password
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user.verify_password(password):
            g.user = user
            return True
        return False

        session['user_id'] = user.id
        return True
    #return False


# This route function requires authentication
# user.genereate_auth_token() generate a serialezied dict {'id':'self.id'} self.id is the user a particular object
# to deserialize the dict use User.verify_auth_token(token) return a self.id = user object


@api.route('/secure')
@auth_api.login_required
def secure_route():
    return 'You are logged in'


@api.route('/get_token')
def get_token():
    s = Serializer('secret-key')
    token = s.dumps('some secret text')
    s = Serializer('secret-key')
    text = s.loads(token)
    return text


@auth_api.error_handler
def auth_error():
    return 'Invalid credentials'