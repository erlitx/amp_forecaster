from flask import Blueprint

# Create a Blueprint object with the name 'main' and the path to the templates
main = Blueprint('main', __name__)

# Import the views module with all the routes
from . import views