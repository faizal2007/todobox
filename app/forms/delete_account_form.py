from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

class DeleteAccountForm(FlaskForm):
    delete_code = StringField('Delete Code', validators=[DataRequired(), Regexp(r'\d+', message='Code must be numeric')])
    submit = SubmitField('Delete Account')
