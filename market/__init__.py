from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf import CSRFProtect


# base directory
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# database creation
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'market.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'b3a7ad096790a5d6213e02a1'

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
bcrypt= Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

    # Importing routes
from market import routes