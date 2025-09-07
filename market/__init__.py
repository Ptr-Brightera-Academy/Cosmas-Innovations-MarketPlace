from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_wtf import CSRFProtect
from functools import wraps
from flask import abort


# base directory
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# database creation
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'market.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
bcrypt= Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_message_category = "info"

@login_manager.unauthorized_handler
def unauthorized_callback():
    if request.path.startswith('/admin'):
        return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('login_page'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

    # Importing routes
from market import routes