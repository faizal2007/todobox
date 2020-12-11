from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, HiddenField
from wtforms.validators import DataRequired, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class ChangePassword(FlaskForm):
    userId = HiddenField()
    oldPassword = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    
    def validate_oldPassword(self, oldPassword):
        user = User.query.filter_by(id=self.userId.data).first()
        if user.check_password(oldPassword.data) == False:
            raise ValidationError('Old Password not match')
   