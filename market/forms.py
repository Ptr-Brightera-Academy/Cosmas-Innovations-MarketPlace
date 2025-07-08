from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from market.models import User

class RegisterForm(FlaskForm):    
    username = StringField(label='User Name',validators=[Length(min=2,max=30), DataRequired()])
    email_address = StringField(label='Email Address', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password',validators=[Length(min=6) , DataRequired()])
    password2 = PasswordField(label='Confirm Password', validators=[EqualTo('password1', message='Passwords must match.'), DataRequired()])
    submit = SubmitField(label='Create Account')
    
    def validate_username(self,username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists')
    
    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email address already exists')
        
class LoginForm(FlaskForm):
    username_or_email = StringField(
        label='Username or Email',
        validators=[DataRequired()]
    )
    password = PasswordField(
        label='Password',
        validators=[DataRequired()]
    )
    submit = SubmitField(label='Log In')

def validate_password(form, field):
    user = User.query.filter(
        (User.username == form.username_or_email.data) |
        (User.email_address == form.username_or_email.data)
    ).first()
    if user is None:
        raise ValidationError("User not found.")
    if not user.check_password_correction(field.data):
        raise ValidationError("Incorrect password.")
    