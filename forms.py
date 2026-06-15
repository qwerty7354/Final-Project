from flask_wtf import FlaskForm
from wtforms.fields import (StringField, PasswordField, IntegerField,
                            SelectField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, ValidationError
from flask_wtf.file import FileField
from models import User


class RegisterForm(FlaskForm):
    username = StringField("Enter Username", validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField("Enter Password", validators=[DataRequired(), Length(min=6, max=24)])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password", message="პაროლები არ ემთხვევა")
    ])
    register = SubmitField("Register")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("ეს username უკვე დაკავებულია.")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    login = SubmitField("Log In")


class BookForm(FlaskForm):
    image = FileField("Upload Book Cover")
    title = StringField("Book Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    year = IntegerField("Publication Year", validators=[DataRequired(), NumberRange(min=0, max=2100)])
    genre = SelectField("Genre", choices=[
        ("Fiction", "Fiction"), ("Non-Fiction", "Non-Fiction"),
        ("Science Fiction", "Science Fiction"), ("Fantasy", "Fantasy"),
        ("Mystery", "Mystery"), ("Biography", "Biography"),
        ("History", "History"), ("Other", "Other"),
    ])
    description = TextAreaField("Description")
    submit = SubmitField("Save Book")


class RatingForm(FlaskForm):
    score = SelectField("Your Rating", choices=[
        (1, "⭐ 1"), (2, "⭐⭐ 2"), (3, "⭐⭐⭐ 3"),
        (4, "⭐⭐⭐⭐ 4"), (5, "⭐⭐⭐⭐⭐ 5")
    ], coerce=int, validators=[DataRequired()])
    submit = SubmitField("Rate")


class SearchForm(FlaskForm):
    q = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("Search")


class CommentForm(FlaskForm):
    text = TextAreaField("Comment", validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField("Post Comment")
