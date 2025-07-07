from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt


# base directory
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# database creation
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'market.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'b3a7ad096790a5d6213e02a1'

db = SQLAlchemy(app)
bcrypt= Bcrypt(app)

from market import routes