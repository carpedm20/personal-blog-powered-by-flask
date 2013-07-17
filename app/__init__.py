#-*- coding: euc-kr -*-
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import basedir, DEBUG, USERNAME, PASSWORD
from momentjs import momentjs
from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.markdown import Markdown

# create our little application :)
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
Markdown(app)

from app import views, models
from jfilter import *
