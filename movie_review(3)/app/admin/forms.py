from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
    widgets,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)
from app.models import User, Genre


class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login to Dashboard')


class UserSearchForm(FlaskForm):
    q = StringField('Search', validators=[])
    role = SelectField('Role', choices=[
        ('all', 'All Roles'),
        ('admin', 'Administrators'),
        ('user', 'Regular Users')
    ])
    status = SelectField('Status', choices=[
        ('all', 'All Status'),
        ('active', 'Active'),
        ('banned', 'Banned')
    ])
    submit = SubmitField('Search')


class UserEditForm(FlaskForm):
    username = StringField(
        'Username', validators=[
            DataRequired(), Length(
                min=2, max=64)])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(
                max=120)])
    is_admin = BooleanField('Is Admin')
    is_active = BooleanField('Is Active')
    submit = SubmitField('Update User')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered.')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=128)])
    year = IntegerField(
        'Year', validators=[
            DataRequired(), NumberRange(
                min=1900, max=2030)])
    director = StringField('Director', validators=[Length(max=64)])
    description = TextAreaField('Description')
    poster_url = StringField(
        'Poster URL', validators=[
            Optional(), Length(
                max=256)])
    genres = MultiCheckboxField('Genres', coerce=int)
    submit = SubmitField('Save Movie')


class MovieSearchForm(FlaskForm):
    q = StringField('Keyword')
    genre = SelectField('Genre', coerce=int, choices=[(0, 'All Genres')])
    year_min = IntegerField('Year From', validators=[Optional()])
    year_max = IntegerField('Year To', validators=[Optional()])
    submit = SubmitField('Search')


class GenreForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('Add Genre')

    def validate_name(self, name):
        genre = Genre.query.filter_by(name=name.data).first()
        if genre:
            raise ValidationError('Genre already exists.')


class ReviewSearchForm(FlaskForm):
    q = StringField('Keyword', validators=[Optional()])
    rating = SelectField('Rating', coerce=int, choices=[
        (0, 'All Ratings'),
        (5, '5 Stars'),
        (4, '4 Stars'),
        (3, '3 Stars'),
        (2, '2 Stars'),
        (1, '1 Star')
    ])
    date_from = DateField(
        'Date From',
        format='%Y-%m-%d',
        validators=[
            Optional()])
    date_to = DateField('Date To', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Search')
