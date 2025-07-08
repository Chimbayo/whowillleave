from flask import Flask
from flask_cors import CORS
from flask_mysqldb import MySQL
from .config import Config
import os

mysql = MySQL()

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    )
    app.config.from_object(Config)
    CORS(app)
    mysql.init_app(app)

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app 