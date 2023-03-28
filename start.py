from app import create_app, db
from config import config

from flask_migrate import Migrate
from app.models import User

config_name = 'development'
app = create_app(config_name)

#Set database migration
migrate = Migrate(app, db)

# @app.shell_context_processor
# def make_shell_context():
#     return dict(db=db)


if __name__ == '__main__':
    app.run(port=config[config_name].PORT, debug=config[config_name].DEBUG)


#set first migration (run in terminal without flask shell)
# pip install flask-migrate
#export FLASK_APP=hello.py

# flask db init
# flask db migrate -m "First migration"
# flask db upgrade




