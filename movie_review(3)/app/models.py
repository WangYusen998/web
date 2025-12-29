from datetime import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer

# 关联表：用户收藏电影
favorites = db.Table(
    'favorites',
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('user.id'),
        primary_key=True),
    db.Column(
        'movie_id',
        db.Integer,
        db.ForeignKey('movie.id'),
        primary_key=True))

# 关联表：电影类型
movie_genres = db.Table(
    'movie_genres',
    db.Column(
        'movie_id',
        db.Integer,
        db.ForeignKey('movie.id'),
        primary_key=True),
    db.Column(
        'genre_id',
        db.Integer,
        db.ForeignKey('genre.id'),
        primary_key=True))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    reviews = db.relationship('Review', backref='author', lazy='dynamic')
    favorited_movies = db.relationship(
        'Movie', secondary=favorites, backref=db.backref(
            'favorited_by', lazy='dynamic'), lazy='dynamic')

    # 设置密码
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_administrator(self):
        return self.is_admin

    def get_reset_password_token(self, expires_in=600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='reset-password')

    @staticmethod
    def verify_reset_password_token(token, expires_in=600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(
                token,
                salt='reset-password',
                max_age=expires_in)['user_id']
        except BaseException:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'<User {self.username}>'


@login.user_loader
def load_user(id):
    user = User.query.get(int(id))
    # If user is banned, deny login/access
    if user and not user.is_active:
        return None
    return user


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return f'<Genre {self.name}>'


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    year = db.Column(db.Integer)
    director = db.Column(db.String(64))
    description = db.Column(db.Text)
    poster_url = db.Column(db.String(256))
    average_rating = db.Column(db.Float, default=0.0)

    # 关系
    reviews = db.relationship('Review', backref='movie', lazy='dynamic')
    genres = db.relationship('Genre', secondary=movie_genres,
                             backref=db.backref('movies', lazy='dynamic'),
                             lazy='dynamic')

    def __repr__(self):
        return f'<Movie {self.title}>'


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))

    def __repr__(self):
        return f'<Review {self.content[:20]}...>'
