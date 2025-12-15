from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, HiddenField
from wtforms.validators import DataRequired, ValidationError, Email, Optional
from app.models import User
from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class SetupAccountForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')
    ])
    fullname = StringField('Full Name')
    submit = SubmitField('Create Account')
    
    def validate_email(self, email):
        try:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Email already in use')
        except Exception:
            # If database is not accessible, skip email uniqueness validation
            # The route will handle database connection errors appropriately
            pass


class RegistrationForm(FlaskForm):
    """Form for user registration with email verification"""
    email = StringField('Email', validators=[DataRequired(), Email(message='Invalid email address')])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')
    ])
    fullname = StringField('Full Name', validators=[Optional()])
    accept_terms = BooleanField('I agree to the Terms of Use and Disclaimer', 
                               validators=[DataRequired(message='You must accept the Terms of Use and Disclaimer to continue')])
    submit = SubmitField('Create Account')
    
    def validate_email(self, email):
        """Check if email is already registered"""
        try:
            user = User.query.filter_by(email=email.data.lower()).first()
            if user is not None:
                raise ValidationError('Email already registered. Please log in or use a different email.')
        except Exception:
            # If database is not accessible, skip email uniqueness validation
            # The route will handle database connection errors appropriately
            pass
    
class ChangePassword(FlaskForm):
    oldPassword = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
        
class UpdateAccount(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    fullname = StringField('Full Name')
    submit = SubmitField('Update Account')

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
        
        # Check if email belongs to an existing user
        user = User.query.filter_by(email=email.data).first()
        if user:
            # If user exists, they must be a Gmail/OAuth user (not a direct login user)
            # Direct login users cannot be invited through sharing
            if user.is_direct_login_user():
                raise ValidationError('This email belongs to a direct login user. You can only invite users with email-based (Google/OAuth) accounts')


class SharingSettingsForm(FlaskForm):
    """Form for managing sharing settings"""
    sharing_enabled = BooleanField('Enable Todo Sharing')
    submit = SubmitField('Save Settings')

class DeleteAccountForm(FlaskForm):
    """Form for account deletion with code verification"""
    delete_code = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Delete Account')