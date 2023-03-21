from config import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from flask_mail import Mail
from flask_moment import Moment

# Initialize the database
db = SQLAlchemy()
mail = Mail()
moment = Moment()


loging_manager = LoginManager()
# Pass to the login view page: auth.login = function "login" in "auth" blueprint
loging_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize the database
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    # Initialize the login manager
    loging_manager.init_app(app)


    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .api import api as api_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    return app