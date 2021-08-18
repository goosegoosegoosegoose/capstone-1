from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length

class CreateUserForm(FlaskForm):
    """Creating user form whoo"""

    username = StringField("Username", validators=[Length(max=16), InputRequired(message="Please enter a username")])
    email = StringField("Email", validators=[Email(message="Please enter a valid email"), InputRequired(message="Please enter your email email")])
    password = PasswordField("Password", validators=[Length(min=5)])
    image_url = StringField("Profile Image - Optional")
    bio = TextAreaField("Bio - Optional")


class LoginForm(FlaskForm):
    """Login user form"""

    username = StringField("Username", validators=[InputRequired(message="Please enter your username")])
    password = PasswordField("Password")

