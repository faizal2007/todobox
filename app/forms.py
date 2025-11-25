from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, HiddenField
from wtforms.validators import DataRequired, ValidationError, Email
from app.models import User
from flask_login import current_user

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class ChangePassword(FlaskForm):
    oldPassword = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
        
class UpdateAccount(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    fullname = StringField('Full Name')
    submit = SubmitField('Update Account')

    def validate_username(self, username):
        # Allow current username, but prevent duplicates
        user = User.query.filter_by(username=username.data).first()
        if user is not None and user.id != current_user.id:
            raise ValidationError('Username already taken')
        
    def validate_email(self, email):
        # Allow current email, but prevent duplicates
        user = User.query.filter_by(email=email.data).first()
        if user is not None and user.id != current_user.id:
            raise ValidationError('Email already in use')