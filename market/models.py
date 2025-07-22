from market import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import JSON

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email_address = db.Column(db.String(255), unique=True, nullable=False)
    email_verified_at = db.Column(db.DateTime)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    products_created = db.relationship('Product', foreign_keys='Product.created_by', backref='creator')
    products_updated = db.relationship('Product', foreign_keys='Product.updated_by', backref='updater')

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(2000), nullable=False)
    slug = db.Column(db.String(2000), nullable=False)
    image = db.Column(db.String(2000))
    image_mime = db.Column(db.String(255))
    image_size = db.Column(db.Integer)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    published = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deleted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deleted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Numeric(20, 2), nullable=False)
    status = db.Column(db.String(45), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Customer(db.Model):
    __tablename__ = 'customers'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(45))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CustomerAddress(db.Model):
    __tablename__ = 'customer_addresses'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(45))
    address1 = db.Column(db.String(255))
    address2 = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(45))
    zipcode = db.Column(db.String(45))
    country_code = db.Column(db.String(3), db.ForeignKey('countries.code'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Country(db.Model):
    __tablename__ = 'countries'
    code = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    states = db.Column(JSON)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(45))
    type = db.Column(db.String(45))
    session_id = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OrderDetail(db.Model):
    __tablename__ = 'order_details'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    phone = db.Column(db.String(45))
    address1 = db.Column(db.String(255))
    address2 = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(45))
    zipcode = db.Column(db.String(45))
    country_code = db.Column(db.String(3))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    email = db.Column(db.String(255), primary_key=True)
    token = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)
