from market import app
from flask import render_template, url_for, flash, redirect, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, ResetRequestForm
from market import db
from flask_login import login_user, logout_user, login_required
from datetime import datetime

# Routes
@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter(
            (User.username == form.username_or_email.data) |
            (User.email_address == form.username_or_email.data)
        ).first()

        if attempted_user and attempted_user.check_password_correction(attempted_password = form.password.data):
            login_user(attempted_user)
            flash('Successfully logged in', category='success')
            return redirect(url_for('market_page')) 
        else:
            flash('Login failed | Wrong credintials.', category='danger')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data 
        )
        db.session.add(user_to_create)
        db.session.commit()
        flash('Account created successfully! You can log in.', category='success')
        return redirect(url_for('login_page'))  

    return render_template('register.html', form=form)

@app.route('/market_sell')
@login_required
def market_page():
    search_query = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Item.query
    if search_query:
        query = query.filter(Item.name.ilike(f"%{search_query}%"))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
        
    return render_template('market.html', items=items)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out.', category='info')
    return redirect(url_for('login_page'))

@app.route('/product_details/<item_id>')
def product_details(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('product_details.html', item=item)

@app.route('/purchase_product')
def purchase_product():
    return render_template('purchase_product.html')

@app.route('/myAccount/lost_password', methods=['GET', 'POST'])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        input_value = form.username_or_email.data
        attempted_user = User.query.filter(
            (User.username == input_value) | (User.email_address == input_value)
            ).first()
        if attempted_user:
            flash('A password reset link has been sent. Please check your email.', category='info')
        else:
            flash('No account found. Please try again.', category='warning')
    return render_template('reset_request.html', form=form)

@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin/dashboard.html", current_year=datetime.now().year)

@app.route("/orders")
def view_orders():
    return render_template("admin/views/orders.html", current_year=datetime.now().year)

@app.route("/users")
def view_users():
    return render_template("admin/views/users.html", current_year=datetime.now().year)

@app.route("/products")
def view_products():
    return render_template("admin/views/products.html", current_year=datetime.now().year)

@app.route("/customers")
def view_customers():
    return render_template("admin/views/customers.html", current_year=datetime.now().year)

@app.route("/reports")
def view_reports():
    return render_template("admin/views/reports.html", current_year=datetime.now().year)

@app.route("/settings")
def admin_settings():
    return render_template("admin/views/settings.html", current_year=datetime.now().year)