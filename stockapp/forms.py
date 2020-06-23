from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField, ValidationError
from wtforms.validators import DataRequired,Length,Email,EqualTo 
from stockapp.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),Length(min=3, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_uername(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(),Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email is not registered.')  

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Reset Password')