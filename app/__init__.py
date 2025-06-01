from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config='default'):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    
    from .main import blue_main
    app.register_blueprint(blue_main)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .messenger import messenger as messenger_blueprint
    app.register_blueprint(messenger_blueprint, url_prefix='/messenger')

    from .subjects import subjects as subjects_blueprint
    app.register_blueprint(subjects_blueprint, url_prefix='/subjects')
    
    return app