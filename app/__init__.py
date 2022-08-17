# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from ctypes import *
from config import Config
from flask_sqlalchemy import SQLAlchemy

login = LoginManager()
login.login_view = 'auth.login'
libc = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libudfdll.so'))
db = SQLAlchemy()
bootstrap = Bootstrap()


def dec64(modelid):
    return str(libc.dec64i0(modelid.encode())) + '_' + str(libc.dec64i1(modelid.encode()))


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    login.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)


    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    return app

from app import models
from app.main import routes

