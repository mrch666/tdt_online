# -*- coding: utf-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap

from config import Config
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
bootstrap = Bootstrap()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    bootstrap.init_app(app)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    return app

from app import models

