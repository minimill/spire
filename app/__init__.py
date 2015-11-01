from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sys import argv
from app.lib.aws import S3

app = None
db = None
s3 = None
login_manager = None


def create_app():
    global app
    global db
    global s3
    global login_manager

    # Flask
    app = Flask(__name__, static_folder='static/dist/', static_url_path='/static')
    app.config.from_object('config.flask_config')

    # SQLAlchemy
    db = SQLAlchemy(app)

    # Amazon S3
    s3 = S3(app)

    # Debug
    app.config['DEBUG'] = (len(argv) == 2 and argv[1] == 'debug')

    from app.routes import register_routes
    register_routes(app, db)

    return app, db
