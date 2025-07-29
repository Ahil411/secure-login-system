from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from app.models import User
import re

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    remember_me = BooleanField('Remember Me')
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters'),
        Regexp(r'^[A-Za-z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address'),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[('User', 'User'), ('Admin', 'Admin')], default='User')
    recaptcha = RecaptchaField()
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

    def validate_password(self, password):
        """Validate password strength"""
        password_val = password.data

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password_val):
            raise ValidationError('Password must contain at least one uppercase letter.')

        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password_val):
            raise ValidationError('Password must contain at least one lowercase letter.')

        # Check for at least one digit
        if not re.search(r'\d', password_val):
            raise ValidationError('Password must contain at least one number.')

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password_val):
            raise ValidationError('Password must contain at least one special character.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    new_password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

    def validate_new_password(self, new_password):
        """Validate password strength"""
        password_val = new_password.data

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password_val):
            raise ValidationError('Password must contain at least one uppercase letter.')

        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password_val):
            raise ValidationError('Password must contain at least one lowercase letter.')

        # Check for at least one digit
        if not re.search(r'\d', password_val):
            raise ValidationError('Password must contain at least one number.')

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password_val):
            raise ValidationError('Password must contain at least one special character.')

class UserManagementForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    role = SelectField('Role', choices=[('User', 'User'), ('Admin', 'Admin')])
    is_active = BooleanField('Active')
    submit = SubmitField('Update User')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    subject = StringField('Subject', validators=[
        DataRequired(),
        Length(min=5, max=100)
    ])
    message = TextAreaField('Message', validators=[
        DataRequired(),
        Length(min=10, max=500)
    ])
    recaptcha = RecaptchaField()
    submit = SubmitField('Send Message')
