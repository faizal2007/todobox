from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, HiddenField
from wtforms.validators import DataRequired, ValidationError, Email, Optional
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


class ShareInvitationForm(FlaskForm):
    """Form for sending sharing invitations"""
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Invitation')
    
    def validate_email(self, email):
        # Cannot invite yourself
        if email.data.lower() == current_user.email.lower():
            raise ValidationError('You cannot invite yourself')
        
        # Check if email belongs to a Gmail user
        user = User.query.filter_by(email=email.data).first()
        if user and not user.is_gmail_user():
            raise ValidationError('This email does not belong to a Gmail/Google account user')


class SharingSettingsForm(FlaskForm):
    """Form for managing sharing settings"""
    sharing_enabled = BooleanField('Enable Todo Sharing')
    submit = SubmitField('Save Settings')