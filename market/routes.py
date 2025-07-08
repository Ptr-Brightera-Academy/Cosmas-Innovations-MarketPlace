from market import app
from flask import render_template, url_for, flash, redirect, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm
from market import db
from flask_login import login_user

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
            flash(f'Successfully logged in', category='success')
            return redirect(url_for('market_page')) 
        else:
            flash('Login failed — Wrong credintials.', category='danger')

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
        flash(f'Account created successfully! You can now log in.', category='success')
        return redirect(url_for('login_page'))  

    return render_template('register.html', form=form)

@app.route('/market_sell')
def market_page():
    items = Item.query.all()
    return render_template('market.html', items=items)