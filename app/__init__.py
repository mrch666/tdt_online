# -*- coding: utf-8 -*-
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)
print(Config.SQLALCHEMY_DATABASE_URI)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

from app import routes
