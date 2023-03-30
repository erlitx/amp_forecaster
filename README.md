# Flask Application

This is a Flask application that sends an API request to the Odoo database 
using the `odoo_rpc_client` library to retrieve information about all products
and locations. The application then composes an HTML page that displays 
information about products that are out of stock in a particular location and 
retrieves the information about the quantities of that product in another 
location.

This application is useful when you have one location associated with online 
sales, and the absence of the products leads to the products being out of 
stock on your online store page.

The app calculates the `availability` of the products as the `quantity on hand` 
minus the `quantity reserved`, resulting in the availability of products at 
the location.

The information about out of stock products for each request is then stored 
permanently in a PostgreSQL database. All the database models are defined and
operated using the `Flask-SQLAlchemy` library.

## Getting Started

To run the application, you will need to install the required dependencies. 
You can do this by running the following command:

`pip install -r requirements.txt`

Once you have installed the dependencies, you can run the application using 
the following command:

`python3 start.py`

The application will start running on http://0.0.0.0:5050/ with configuration
from the `config.py` file. 

In order to select configuration type change 
`config_name = 'development'`
to `production` or `development`.

## Configuration
#### (config.py)
###### Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    
###### Mail Sender Configuration

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')  
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))`
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Master Forecaster]'
    FLASKY_MAIL_SENDER = 'Master Forecaster'

#### (.env)
###### Database Configuration
    SQLALCHEMY_DATABASE_URI='postgresql://<user_name>:<password>@<localhost:5432>/<db_name>'

###### Email account credentials
    MAIL_USERNAME=<email_address>
    MAIL_PASSWORD=<password>

###### Odoo account credentials
    HOST=<url_to_odoo>
    PORT=<port>
    DATABASE=<production, staging or development>
    ODOO_USERNAME=<odoo_username>
    ODOO_PASSWORD=<odoo_password>

###### Scheduler Configuration (how often to send API requests to Odoo)
    INTERVAL_MINUTES=<int: minutes between each scheduler run>

## Routes

The application has the following routes:

###### (main routes)

### `/`
This route sends an API request to Odoo database using the `odoo_rpc_client` library to retrieve information about all products and locations. The application then composes an HTML page that displays information about products that are out of stock in a particular location.

###### (authentication routes, optional)
### `/auth/register_user`

This route handles user registration. Users can create a new account by providing their email address and password.

### `/auth/login`

This route handles user authentication. Users can log in to their account by providing their email address and password.


## License

This application is licensed under the MIT License. See LICENSE for more information.

## Authors

- Mikhail Belogortsev (https://github.com/erlitx)