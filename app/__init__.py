# -*- coding: utf-8 -*-

'''app/__init__.py'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config


db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'

csrf = CSRFProtect()


def create_app(config_name):
    '''__init__.create_app(config_name)'''

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint, url_prefix='/profile')

    from .study import study as study_blueprint
    app.register_blueprint(study_blueprint, url_prefix='/study')

    from .demo import demo as demo_blueprint
    app.register_blueprint(demo_blueprint, url_prefix='/demo')

    from .status import status as status_blueprint
    app.register_blueprint(status_blueprint, url_prefix='/status')

    from .manage import manage as manage_blueprint
    app.register_blueprint(manage_blueprint, url_prefix='/manage')

    from .resource import resource as resource_blueprint
    app.register_blueprint(resource_blueprint, url_prefix='/resource')

    from .develop import develop as develop_blueprint
    app.register_blueprint(develop_blueprint, url_prefix='/develop')

    from .search import search as search_blueprint
    app.register_blueprint(search_blueprint, url_prefix='/search')

    return app
