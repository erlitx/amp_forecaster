from flask import Blueprint


api = Blueprint('api', __name__)

from . import users, authentication, inventory, saleable_stock
