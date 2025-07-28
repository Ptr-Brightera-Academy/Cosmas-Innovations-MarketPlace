from market import app, db, bcrypt, login_manager
from flask import render_template, url_for, flash, redirect, request
from werkzeug.utils import secure_filename
from market.models import Product, User
from market.forms import RegisterForm, LoginForm, ResetRequestForm, ProductForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import os
import slugify 
from slugify import slugify

# Routes
@app.route('/')
def home_page():
    products = Product.query.filter_by(published=True).order_by(Product.created_at.desc()).all()
    return render_template('users/views/home.html', products =products, title_class="text-white")

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
            return redirect(url_for('market_page')) 
        else:
            flash('Login failed | Wrong credintials.', category='danger')

    return render_template('users/auth/login.html', form=form)

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

    return render_template('users/auth/register.html', form=form)

@app.route('/products/market/')
@login_required
def market_page():
    products = Product.query.filter_by(published=True).order_by(Product.created_at.desc()).all()
    search_query = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Product.query
    if search_query:
        query = query.filter(Product.title.ilike(f"%{search_query}%"))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        products = pagination.items
        
    return render_template('users/views/market.html', products =products, title_class="text-dark")

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out.', category='info')
    return redirect(url_for('login_page'))

@app.route('/product_details/<slug>')
def product_details(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    return render_template('users/views/product_details.html', product=product)

@app.route('/cart/view')
def cart_page():
    return render_template('users/views/cart_items.html')

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
    return render_template('users/auth/reset_request.html', form=form)

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    return render_template("admin/views/dashboard.html", current_year=datetime.now().year)

@app.route("/admin/view/orders")
@login_required
def view_orders():
    return render_template("admin/views/orders.html", current_year=datetime.now().year)

@app.route("/admin/view/users")
@login_required
def admin_users():
    users = User.query.all()
    return render_template("admin/views/users.html", current_year=datetime.now().year, users=users)

@app.route('/admin/users/edit/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    new_username = request.form.get('username')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    errors = {}

    # Check for duplicate username
    if new_username and new_username != user.username:
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            errors['username'] = "Username already taken"
        else:
            user.username = new_username

    # Handle password change
    if old_password or new_password or confirm_password:
        if not old_password:
            errors['old_password'] = "Old password is required"
        elif not bcrypt.check_password_hash(user.password_hash, old_password):
            errors['old_password'] = "Old password is incorrect"
        elif new_password != confirm_password:
            errors['new_password'] = "New passwords do not match"
        elif not new_password:
            errors['new_password'] = "New password cannot be empty"
        else:
            user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

    if errors:
        users = User.query.all()
        return render_template("admin/views/users.html", users=users, edit_errors=errors, active_modal_user_id=user.id)

    db.session.commit()
    return redirect(url_for('admin_users'))


@app.route('/admin/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash(f'User "{user_to_delete.username}" was successfully deleted.', 'success')
        return redirect(url_for('admin_users'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the user.', 'danger')
        return redirect(url_for('admin_users'))

@app.route("/admin/view/products")
@login_required
def view_products():
    products = Product.query.order_by(Product.updated_at.desc()).all()
    form = ProductForm()
    return render_template("admin/views/products.html",
     current_year = datetime.now().year, 
     form = form,
     products = products)

@app.route("/admin/view/customers")
@login_required
def view_customers():
    return render_template("admin/views/customers.html", current_year=datetime.now().year)

@app.route("/admin/view/reports")
@login_required
def view_reports():
    return render_template("admin/views/reports.html", current_year=datetime.now().year)

@app.route("/admin/settings")
@login_required
def admin_settings():
    return render_template("admin/views/settings.html", current_year=datetime.now().year)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username_or_email.data
        password = form.password.data

        user = User.query.filter(
            (User.email_address == identifier) | (User.username == identifier)
        ).first()

        if user and user.check_password_correction(password):
            if user.is_admin:
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            else:
                flash("You do not have permission to access the admin panel.", category='danger')
        else:
            flash("Username/email or password is incorrect.", category='danger')

    return render_template("admin/auth/login.html", form=form)


@app.route('/admin/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/myAccount/resetPassword')
def password_reset():
    return render_template("admin/auth/reset_password.html")


UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/products/create', methods=['GET', 'POST'])
@login_required
def create_product():
    form = ProductForm()
    if request.method == 'POST':
        title = request.form.get('title')
        price = request.form.get('price')
        description = request.form.get('description')
        image = request.files.get('image')

        slug = slugify(title)
        image_url = None
        image_mime = None
        image_size = None

        if image and image.filename:
            filename = secure_filename(image.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            image.save(save_path)

            image_url = url_for('static', filename=f'uploads/{filename}')
            image_mime = image.mimetype
            image_size = os.path.getsize(save_path)

        product = Product(
            title=title,
            slug=slug,
            price=price,
            description=description,
            image=image_url,
            image_mime=image_mime,
            image_size=image_size,
            created_by=current_user.id,
            updated_by=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(product)
        db.session.commit()

        flash('Product created successfully!', 'success')
        return redirect(url_for('view_products')) 

    return  render_template("admin/views/products.html", current_year=datetime.now().year, form=form)

def allowed_file(fname):
    return '.' in fname and fname.rsplit('.',1)[1].lower() in {'png','jpg','jpeg','gif'}

@app.route('/admin/products/edit/<int:id>', methods=['POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    product.title = request.form.get('title')
    product.price = request.form.get('price')
    product.description = request.form.get('description')
    product.slug = slugify(product.title)
    product.updated_by = current_user.id
    product.updated_at = datetime.utcnow()

    image = request.files.get('image')
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        image.save(save_path)
        product.image = url_for('static', filename=f'uploads/{filename}')
        product.image_mime = image.mimetype
        product.image_size = os.path.getsize(save_path)

    db.session.commit()
    flash('Product updated successfully!', 'success')
    return redirect(url_for('view_products'))

@app.route('/admin/products/delete/<int:id>', methods=['GET'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'danger')
    return redirect(url_for('view_products'))

@app.route('/product/<slug>')
def products_view(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    return render_template('users/views/products.html', product=product)