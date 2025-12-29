from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        'Username', validators=[
            DataRequired(), Length(
                min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField(
        'Password', validators=[
            DataRequired(), Length(
                min=6)])
    confirm_password = PasswordField(
        'Confirm Password', validators=[
            DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # 验证用户名是否存在
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Username is already taken. Please choose a different one.')

    # 验证邮箱是否存在
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'Email is already registered. Please use a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'Password', validators=[
            DataRequired(), Length(
                min=6)])
    confirm_password = PasswordField(
        'Confirm Password', validators=[
            DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class ReviewForm(FlaskForm):
    content = TextAreaField(
        'Review Content', validators=[
            DataRequired(), Length(
                min=10, max=500)])
    rating = SelectField(
        'Rating',
        choices=[
            (1,
             '1 Star'),
            (2,
             '2 Stars'),
            (3,
             '3 Stars'),
            (4,
             '4 Stars'),
            (5,
             '5 Stars')],
        coerce=int,
        validators=[
            DataRequired()])
    submit = SubmitField('Submit Review')


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[])
    genre = SelectField('Genre', choices=[], coerce=int)
    submit = SubmitField('Search')
