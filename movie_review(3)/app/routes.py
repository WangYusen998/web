from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from sqlalchemy import desc, or_, func
from app import db, limiter
from app.models import User, Movie, Review, Genre
from app.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
    ReviewForm,
)
from app.logger import auth_logger, error_logger, log_auth, log_db

main = Blueprint('main', __name__)

# Home page route


@main.route('/')
def index():
    # 获取最新评论的电影
    latest_reviews = Review.query.order_by(
        desc(Review.created_at)).limit(30).all()
    latest_movies = [review.movie for review in latest_reviews]
    # 去重
    latest_movies = list(dict.fromkeys(latest_movies))[:10]

    # 获取评分最高的电影
    top_rated_movies = Movie.query.order_by(
        desc(Movie.average_rating)).limit(10).all()

    recommended_movies = []
    if current_user.is_authenticated:
        # 简单的推荐逻辑：基于用户收藏的电影类型
        user_favorites = current_user.favorited_movies.all()
        if user_favorites:
            favorite_genres = set()
            for movie in user_favorites:
                for genre in movie.genres:
                    favorite_genres.add(genre.id)

            if favorite_genres:
                recommended_movies = (
                    Movie.query.filter(
                        Movie.genres.any(Genre.id.in_(favorite_genres))
                    )
                    .filter(~Movie.id.in_([m.id for m in user_favorites]))
                    .limit(10)
                    .all()
                )

    return render_template(
        'index.html',
        latest_movies=latest_movies,
        top_rated_movies=top_rated_movies,
        recommended_movies=recommended_movies)


@main.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    genre_id = request.args.get('genre', type=int)
    year_min = request.args.get('year_min', type=int)
    year_max = request.args.get('year_max', type=int)
    sort_by = request.args.get('sort_by', 'rating')  # rating, year, favorites
    order = request.args.get('order', 'desc')  # desc, asc

    query = Movie.query

    # Search (Title or Director)
    if search_query:
        query = query.filter(or_(
            Movie.title.ilike(f'%{search_query}%'),
            Movie.director.ilike(f'%{search_query}%')
        ))

    # Filter by Genre
    if genre_id:
        query = query.filter(Movie.genres.any(Genre.id == genre_id))

    # Filter by Year Range
    if year_min:
        query = query.filter(Movie.year >= year_min)
    if year_max:
        query = query.filter(Movie.year <= year_max)

    # Sorting
    if sort_by == 'favorites':
        # Join with favorited_by relationship and count
        # We use outerjoin to include movies with 0 favorites
        query = query.outerjoin(Movie.favorited_by).group_by(Movie.id)
        if order == 'asc':
            query = query.order_by(func.count(User.id).asc())
        else:
            query = query.order_by(func.count(User.id).desc())
    elif sort_by == 'year':
        if order == 'asc':
            query = query.order_by(Movie.year.asc())
        else:
            query = query.order_by(Movie.year.desc())
    else:  # Default: rating
        if order == 'asc':
            query = query.order_by(Movie.average_rating.asc())
        else:
            query = query.order_by(Movie.average_rating.desc())

    movies_pagination = query.paginate(
        page=page,
        per_page=15,
        error_out=False
    )

    # 获取所有类型用于筛选
    genres = Genre.query.all()

    return render_template(
        'movies.html',
        movies=movies_pagination,
        genres=genres,
        current_genre=genre_id,
        search_query=search_query,
        year_min=year_min,
        year_max=year_max,
        sort_by=sort_by,
        order=order
    )


@main.route('/movie/<int:id>')
def movie(id):
    movie = Movie.query.get_or_404(id)
    reviews = movie.reviews.order_by(desc(Review.created_at)).all()
    form = ReviewForm()
    return render_template(
        'movie_detail.html',
        movie=movie,
        reviews=reviews,
        form=form)


@main.route('/movie/<int:id>/review', methods=['POST'])
@login_required
def add_review(id):
    movie = Movie.query.get_or_404(id)
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            content=form.content.data,
            rating=form.rating.data,
            author=current_user,
            movie=movie)
        db.session.add(review)

        # 更新电影平均评分
        all_reviews = movie.reviews.all()
        total_score = sum([r.rating for r in all_reviews]) + form.rating.data
        movie.average_rating = total_score / (len(all_reviews) + 1)

        try:
            db.session.commit()

            # Log Review Add
            log_db(
                'add',
                'review',
                record_id=review.id,
                name=movie.title,
                operator=current_user,
                details={
                    '评分': form.rating.data})

            flash('Your review has been posted!')
        except Exception as e:
            db.session.rollback()
            error_logger.exception(f'数据库操作失败 (添加评论): {e}')
            flash('操作失败，请重试', 'error')

    return redirect(url_for('main.movie', id=movie.id))


@main.route('/my-favorites')
@login_required
def my_favorites():
    favorites = current_user.favorited_movies.all()
    return render_template('my_favorites.html', favorites=favorites)


@main.route('/my-reviews')
@login_required
def my_reviews():
    reviews = current_user.reviews.order_by(desc(Review.created_at)).all()
    return render_template('my_reviews.html', reviews=reviews)


@main.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # 自动登录
        login_user(user)

        # Log Success
        log_auth('register', user=user, success=True)

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.index'))
    elif request.method == 'POST':
        # Log Failure
        reasons = []
        for field, errors in form.errors.items():
            for error in errors:
                reasons.append(f"{field}: {error}")
        reason_str = ", ".join(reasons)
        log_auth(
            'register',
            email=form.email.data,
            success=False,
            reason=reason_str)

    return render_template('register.html', title='Register', form=form)


@main.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            # Log Failure
            reason = "用户不存在" if user is None else "密码错误"
            log_auth(
                'login',
                email=form.email.data,
                success=False,
                reason=reason)

            flash('Invalid email or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)

        # Log Success
        log_auth('login', user=user, success=True)

        next_page = request.args.get('next')
        # 如果next_page不存在或包含完整的URL（包含域名），则重定向到index
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@main.route('/logout')
def logout():
    # Log Logout
    if current_user.is_authenticated:
        auth_logger.info(
            '[AUTH] 用户登出 - 用户名:%s, IP:%s',
            current_user.username,
            request.remote_addr
        )

    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

# AJAX API Endpoints


@main.route('/api/favorite/<int:movie_id>', methods=['POST'])
@login_required
def favorite_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie in current_user.favorited_movies:
        current_user.favorited_movies.remove(movie)
        favorited = False
    else:
        current_user.favorited_movies.append(movie)
        favorited = True

    try:
        db.session.commit()

        # Log Wishlist Action
        log_action = 'add' if favorited else 'delete'
        log_db(log_action, 'favorite', name=movie.title, operator=current_user)

        return jsonify({
            'success': True,
            'favorited': favorited,
            'favorite_count': movie.favorited_by.count()
        })
    except Exception as e:
        db.session.rollback()
        error_logger.exception(f'数据库操作失败 (收藏操作): {e}')
        return jsonify({'success': False, 'message': 'Operation failed'}), 500


@main.route('/api/movie/<int:movie_id>/reviews')
def get_movie_reviews(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    reviews_pagination = movie.reviews.order_by(
        desc(Review.created_at)
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    reviews_data = []
    for review in reviews_pagination.items:
        reviews_data.append({
            'id': review.id,
            'content': review.content,
            'rating': review.rating,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'author': review.author.username
        })

    return jsonify(
        {
            'reviews': reviews_data,
            'has_next': reviews_pagination.has_next,
            'next_page': (
                reviews_pagination.next_num
                if reviews_pagination.has_next
                else None
            ),
            'total': reviews_pagination.total,
        }
    )


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    reset_url = url_for('main.reset_password', token=token, _external=True)
    # For development/demo purposes, print to console
    print("\n" + "=" * 50)
    print(f"Password reset requested for {user.email}")
    print(f"Reset URL: {reset_url}")
    print("=" * 50 + "\n")


@main.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # In a real app, we would send an email here.
            # send_password_reset_email(user)
            # For this demo, we'll redirect directly to the reset page
            token = user.get_reset_password_token()
            flash(
                'Demo mode: Redirecting directly to password reset page.',
                'info'
            )
            return redirect(url_for('main.reset_password', token=token))
        flash('Email not found.', 'error')
        return redirect(url_for('main.reset_password_request'))
    return render_template(
        'reset_password_request.html',
        title='Reset Password',
        form=form
    )


@main.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid or expired reset link')
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        try:
            db.session.commit()
            flash('Your password has been reset.')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            error_logger.exception(f'数据库操作失败 (重置密码): {e}')
            flash('操作失败，请重试', 'error')
    return render_template('reset_password.html', form=form)
