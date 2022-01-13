from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import validators


class SignUpForm(FlaskForm):
    username = StringField('Username', validators = [validators.DataRequired()])
    password = StringField('password', validators = [validators.DataRequired()])
    register = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators = [validators.DataRequired()])
    password = StringField('password', validators = [validators.DataRequired()])
    login = SubmitField('Login')

