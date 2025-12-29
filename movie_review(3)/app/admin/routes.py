import os
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_

from app import db
from app.admin import bp
from app.admin.forms import (
    AdminLoginForm,
    GenreForm,
    MovieForm,
    MovieSearchForm,
    ReviewSearchForm,
    UserEditForm,
    UserSearchForm,
)
from app.logger import db_logger, admin_logger, error_logger, log_admin, log_db
from app.models import Genre, Movie, Review, User


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if (
            not current_user.is_authenticated
            or not current_user.is_administrator()
        ):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_administrator():
            return redirect(url_for('admin.index'))
        flash('You do not have permission to access the admin panel.', 'error')
        return redirect(url_for('main.index'))

    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.is_administrator():
                # Make session permanent for timeout config to work
                session.permanent = True
                login_user(user)

                # Log Admin Login Success
                log_admin('管理员登录', user)

                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('admin.index')
                return redirect(next_page)
            else:
                # Log Admin Login Failure (Not Admin)
                details = f"原因:非管理员账户, 邮箱:{form.email.data}"
                log_admin('管理员登录失败', user, details=details)
                flash(
                    'You do not have permission to access the admin panel.',
                    'error')
        else:
            # Log Admin Login Failure (Invalid Credentials)
            class MockUser:
                username = 'Unknown'

            mock_user = user if user else MockUser()
            details = f"邮箱:{form.email.data}, 原因:用户名或密码错误"
            log_admin('管理员登录失败', mock_user, details=details)

            flash('Invalid email or password', 'error')

    return render_template('admin/login.html', title='Admin Login', form=form)


@bp.route('/logout')
def logout():
    # Log Admin Logout
    if current_user.is_authenticated:
        log_admin('管理员登出', current_user)

    logout_user()
    return redirect(url_for('admin.login'))


@bp.route('/')
@bp.route('/dashboard')
@admin_required
def index():
    # 统计数据
    today = datetime.utcnow().date()

    stats = {
        'total_users': User.query.count(),
        'total_movies': Movie.query.count(),
        'total_reviews': Review.query.count(),
        'new_users_today': User.query.filter(User.created_at >= today).count()
    }

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_reviews = Review.query.order_by(
        Review.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           title='Dashboard',
                           stats=stats,
                           recent_users=recent_users,
                           recent_reviews=recent_reviews)


@bp.route('/users')
@admin_required
def users_list():
    # Log Admin Access
    log_admin('访问用户管理页面', current_user)

    page = request.args.get('page', 1, type=int)
    # Enable CSRF protection for search form
    form = UserSearchForm(request.args)

    query = User.query

    # 搜索
    if form.q.data:
        search_term = f"%{form.q.data}%"
        query = query.filter(or_(
            User.username.like(search_term),
            User.email.like(search_term)
        ))

    # 角色筛选
    if form.role.data and form.role.data != 'all':
        if form.role.data == 'admin':
            query = query.filter_by(is_admin=True)
        elif form.role.data == 'user':
            query = query.filter_by(is_admin=False)

    # 状态筛选
    if form.status.data and form.status.data != 'all':
        if form.status.data == 'active':
            query = query.filter_by(is_active=True)
        elif form.status.data == 'banned':
            query = query.filter_by(is_active=False)

    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False)

    return render_template(
        'admin/users/list.html',
        title='User Management',
        users=users,
        form=form
    )


@bp.route('/users/<int:id>')
@admin_required
def user_detail(id):
    user = User.query.get_or_404(id)
    reviews = user.reviews.order_by(Review.created_at.desc()).all()
    favorites = user.favorited_movies.all()
    title = f"User: {user.username}"
    return render_template(
        'admin/users/detail.html',
        title=title,
        user=user,
        reviews=reviews,
        favorites=favorites
    )


@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserEditForm(
        original_username=user.username,
        original_email=user.email,
        obj=user)

    if form.validate_on_submit():
        # Prevent self or super admin de-admining or banning
        if user.id == current_user.id:
            if not form.is_admin.data:
                flash('Cannot remove admin privileges from yourself.', 'error')
                return redirect(url_for('admin.edit_user', id=id))
            if not form.is_active.data:
                flash('Cannot ban yourself.', 'error')
                return redirect(url_for('admin.edit_user', id=id))

        if user.email == 'admin@admin.com':
            if not form.is_admin.data:
                flash(
                    'Cannot remove admin privileges from Super Admin.',
                    'error'
                )
                return redirect(url_for('admin.edit_user', id=id))
            if not form.is_active.data:
                flash('Cannot ban Super Admin.', 'error')
                return redirect(url_for('admin.edit_user', id=id))

        # Capture changes for logging
        changes = []
        if user.is_admin != form.is_admin.data:
            changes.append("设为管理员" if form.is_admin.data else "取消管理员")
        if user.is_active != form.is_active.data:
            changes.append("激活用户" if form.is_active.data else "禁用用户")
        if user.username != form.username.data:
            changes.append(f"用户名变更为{form.username.data}")
        if not changes:
            changes.append("基本信息修改")
        change_str = ", ".join(changes)

        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        db.session.commit()

        # Log User Edit
        log_db(
            'edit',
            'user',
            name=user.username,
            operator=current_user,
            details=change_str)

        flash(f'User {user.username} has been updated.', 'success')
        return redirect(url_for('admin.users_list'))

    return render_template(
        'admin/users/edit.html',
        title='Edit User',
        form=form,
        user=user
    )


@bp.route('/users/<int:id>/delete', methods=['POST'])
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash('Cannot delete yourself.', 'error')
        return redirect(url_for('admin.users_list'))

    # 保护超级管理员账号
    if user.email == 'admin@admin.com':
        flash('Cannot delete Super Admin account.', 'error')
        return redirect(url_for('admin.users_list'))

    # 删除关联数据（评论、收藏会自动处理或需手动处理，取决于模型设置）
    # 这里我们手动清理关联关系以确保安全
    user.reviews.delete()
    # 清空收藏关联
    user.favorited_movies = []

    username_to_delete = user.username

    try:
        db.session.delete(user)
        db.session.commit()
        # Log User Delete
        log_db(
            'delete',
            'user',
            name=username_to_delete,
            operator=current_user)
        flash(f'User {username_to_delete} has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        error_logger.exception(f'数据库操作失败 (删除用户): {e}')
        flash('操作失败，请重试', 'error')

    return redirect(url_for('admin.users_list'))


@bp.route('/users/<int:id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(id):
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        return jsonify({'success': False,
                        'message': 'Cannot change your own status'})

    if user.email == 'admin@admin.com':
        return jsonify({'success': False,
                        'message': 'Cannot change Super Admin status'})

    user.is_active = not user.is_active
    db.session.commit()

    status_text = 'active' if user.is_active else 'banned'

    # Log User Status Change
    log_action = "enable" if user.is_active else "disable"
    log_db(log_action, 'user', name=user.username, operator=current_user)

    return jsonify({
        'success': True,
        'is_active': user.is_active,
        'message': f'User {user.username} is now {status_text}'
    })

# Movie Management


@bp.route('/movies')
@admin_required
def movies_list():
    page = request.args.get('page', 1, type=int)
    # Enable CSRF protection for search form
    form = MovieSearchForm(request.args)

    query = Movie.query  # Populate genre choices for search
    genres = Genre.query.order_by(Genre.name).all()
    form.genre.choices = [(0, 'All Genres')] + [(g.id, g.name) for g in genres]

    query = Movie.query

    if form.q.data:
        search_term = f"%{form.q.data}%"
        query = query.filter(or_(
            Movie.title.like(search_term),
            Movie.director.like(search_term)
        ))

    if form.genre.data and form.genre.data != 0:
        query = query.filter(Movie.genres.any(Genre.id == form.genre.data))

    if form.year_min.data:
        query = query.filter(Movie.year >= form.year_min.data)

    if form.year_max.data:
        query = query.filter(Movie.year <= form.year_max.data)

    movies = query.order_by(Movie.year.desc()).paginate(
        page=page, per_page=15, error_out=False)

    return render_template(
        'admin/movies/list.html',
        title='Movies',
        movies=movies,
        form=form)


@bp.route('/movies/add', methods=['GET', 'POST'])
@admin_required
def movie_add():
    form = MovieForm()
    # Populate genre choices
    form.genres.choices = [(g.id, g.name)
                           for g in Genre.query.order_by(Genre.name).all()]

    if form.validate_on_submit():
        movie = Movie(
            title=form.title.data,
            year=form.year.data,
            director=form.director.data,
            description=form.description.data,
            poster_url=form.poster_url.data
        )

        # Add genres
        selected_genres = Genre.query.filter(
            Genre.id.in_(form.genres.data)).all()
        movie.genres.extend(selected_genres)

        db.session.add(movie)
        db.session.commit()

        # Log Movie Add
        log_db('add', 'movie', name=movie.title, operator=current_user)

        flash(f'Movie "{movie.title}" has been created.', 'success')
        return redirect(url_for('admin.movies_list'))

    return render_template(
        'admin/movies/form.html',
        title='Add Movie',
        form=form)


@bp.route('/movies/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def movie_edit(id):
    movie = Movie.query.get_or_404(id)
    form = MovieForm(obj=movie)

    # Populate genre choices
    form.genres.choices = [(g.id, g.name)
                           for g in Genre.query.order_by(Genre.name).all()]

    if request.method == 'GET':
        # Pre-select genres
        form.genres.data = [g.id for g in movie.genres]

    if form.validate_on_submit():
        form.populate_obj(movie)

        # Update genres
        movie.genres = []  # Clear existing
        selected_genres = Genre.query.filter(
            Genre.id.in_(form.genres.data)).all()
        movie.genres.extend(selected_genres)

        db.session.commit()

        # Log Movie Edit
        log_db(
            'edit',
            'movie',
            record_id=movie.id,
            name=movie.title,
            operator=current_user)

        flash(f'Movie "{movie.title}" has been updated.', 'success')
        return redirect(url_for('admin.movies_list'))

    return render_template(
        'admin/movies/form.html',
        title='Edit Movie',
        form=form,
        movie=movie)


@bp.route('/movies/<int:id>/delete', methods=['POST'])
@admin_required
def movie_delete(id):
    movie = Movie.query.get_or_404(id)

    # Delete related reviews
    Review.query.filter_by(movie_id=id).delete()

    # Clear genre associations
    movie.genres = []

    movie_id = movie.id
    movie_title = movie.title

    try:
        db.session.delete(movie)
        db.session.commit()
        # Log Movie Delete
        db_logger.warning(
            '[DB] 电影删除 - ID:%s, 标题:%s, 操作者:%s, IP:%s',
            movie_id,
            movie_title,
            current_user.username,
            request.remote_addr
        )
        flash('Movie deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        error_logger.exception(f'数据库操作失败 (删除电影): {e}')
        flash('操作失败，请重试', 'error')

    return redirect(url_for('admin.movies_list'))

# Genre Management


@bp.route('/genres', methods=['GET', 'POST'])
@admin_required
def genres_list():
    form = GenreForm()
    if form.validate_on_submit():
        genre = Genre(name=form.name.data)
        db.session.add(genre)
        try:
            db.session.commit()
            flash(f'Genre "{genre.name}" added.', 'success')
            return redirect(url_for('admin.genres_list'))
        except Exception as e:
            db.session.rollback()
            error_logger.exception(f'数据库操作失败 (添加类型): {e}')
            flash('操作失败，请重试', 'error')

    genres = Genre.query.order_by(Genre.name).all()
    return render_template('admin/genres.html', form=form, genres=genres)

# Review Management


@bp.route('/reviews')
@admin_required
def reviews_list():
    page = request.args.get('page', 1, type=int)
    # Enable CSRF protection for search form
    form = ReviewSearchForm(request.args)

    query = Review.query

    # Keyword search (content)
    if form.q.data:
        query = query.filter(Review.content.like(f"%{form.q.data}%"))

    # Rating filter
    if form.rating.data and form.rating.data != 0:
        query = query.filter_by(rating=form.rating.data)

    # Date range filter
    if form.date_from.data:
        query = query.filter(Review.created_at >= form.date_from.data)

    if form.date_to.data:
        # Add one day to include the end date fully (since datetime comparison)
        end_date = form.date_to.data + timedelta(days=1)
        query = query.filter(Review.created_at < end_date)

    reviews = query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False)

    return render_template(
        'admin/reviews/list.html',
        title='Reviews',
        reviews=reviews,
        form=form)


@bp.route('/reviews/<int:id>')
@admin_required
def review_detail(id):
    review = Review.query.get_or_404(id)
    return render_template(
        'admin/reviews/detail.html',
        title='Review Detail',
        review=review)


@bp.route('/reviews/<int:id>/delete', methods=['POST'])
@admin_required
def review_delete(id):
    review = Review.query.get_or_404(id)
    movie = review.movie

    try:
        db.session.delete(review)
        db.session.commit()
        # Recalculate movie average rating
        update_movie_rating(movie)
        flash('Review deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        error_logger.exception(f'数据库操作失败 (删除评论): {e}')
        flash('操作失败，请重试', 'error')

    return redirect(url_for('admin.reviews_list'))


@bp.route('/reviews/batch-delete', methods=['POST'])
@admin_required
def reviews_batch_delete():
    review_ids = request.form.getlist('review_ids')
    if not review_ids:
        flash('No reviews selected.', 'warning')
        return redirect(url_for('admin.reviews_list'))

    # Convert IDs to integers
    try:
        review_ids = [int(rid) for rid in review_ids]
    except ValueError:
        flash('Invalid review IDs.', 'error')
        return redirect(url_for('admin.reviews_list'))

    reviews = Review.query.filter(Review.id.in_(review_ids)).all()
    affected_movies = set()

    for review in reviews:
        affected_movies.add(review.movie)

        # Log individual review delete in batch
        db_logger.warning(
            '[DB] 评论删除 (批量) - 评论ID:%s, 电影:%s, 原作者:%s, 操作者:%s, IP:%s',
            review.id,
            review.movie.title,
            review.author.username,
            current_user.username,
            request.remote_addr
        )

        db.session.delete(review)

    db.session.commit()

    # Log Batch Delete Summary
    admin_logger.warning(
        '[ADMIN] 批量删除评论 - 数量:%s, 操作者:%s, IP:%s',
        len(reviews),
        current_user.username,
        request.remote_addr
    )

    # Update ratings for affected movies
    for movie in affected_movies:
        update_movie_rating(movie)

    flash(f'{len(reviews)} reviews deleted.', 'success')
    return redirect(url_for('admin.reviews_list'))


def update_movie_rating(movie):
    """Recalculate and update average rating for a movie"""
    reviews = movie.reviews.all()
    if reviews:
        avg = sum(r.rating for r in reviews) / len(reviews)
        movie.average_rating = avg
    else:
        movie.average_rating = 0.0
    db.session.commit()

    # Kept to show explicit behavior; no template rendering in this helper.


@bp.route('/genres/<int:id>/delete', methods=['POST'])
@admin_required
def genre_delete(id):
    genre = Genre.query.get_or_404(id)
    # Check if used by any movie
    if genre.movies.count() > 0:
        flash('Cannot delete genre that is assigned to movies.', 'error')
    else:
        db.session.delete(genre)
        db.session.commit()
        flash('Genre deleted.', 'success')
    return redirect(url_for('admin.genres_list'))


@bp.route('/logs')
@admin_required
def logs_list():
    # 1. Get log files
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__))))
    log_dir = os.path.join(base_dir, 'logs')

    if not os.path.exists(log_dir):
        flash('Log directory not found.', 'error')
        return redirect(url_for('admin.index'))

    log_files = []
    try:
        all_files = os.listdir(log_dir)
        for f in all_files:
            if f.endswith('.log') or '.log.' in f:
                log_files.append(f)
        log_files.sort(reverse=True)  # Newest first
    except Exception as e:
        error_logger.exception(f"Error listing log files: {e}")
        flash('Error listing log files.', 'error')
        return redirect(url_for('admin.index'))

    # 2. Determine which file to read
    selected_file = request.args.get('file', 'app.log')

    # Security check: ensure file is in log_files or is app.log
    if selected_file not in log_files and selected_file != 'app.log':
        # If requested file is not in list, fall back to app.log if possible.
        if 'app.log' in log_files:
            selected_file = 'app.log'
        elif log_files:
            selected_file = log_files[0]
        else:
            selected_file = None

    # 3. Read and filter content
    log_content = []
    level_filter = request.args.get('level')
    keyword = request.args.get('q')

    if selected_file:
        try:
            file_path = os.path.join(log_dir, selected_file)
            if os.path.exists(file_path):
                with open(
                    file_path,
                    'r',
                    encoding='utf-8',
                    errors='replace'
                ) as f:
                    lines = f.readlines()

                # Reverse for display (newest top)
                lines.reverse()

                for line in lines:
                    # Filter by level
                    if level_filter and f"[{level_filter}]" not in line:
                        continue
                    # Filter by keyword
                    if keyword and keyword.lower() not in line.lower():
                        continue

                    log_content.append(line.strip())
        except Exception as e:
            error_logger.exception(
                f"Error reading log file {selected_file}: {e}")
            flash(f'Error reading log file: {selected_file}', 'error')

    # 4. Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 100
    total_lines = len(log_content)
    start = (page - 1) * per_page
    end = start + per_page

    current_logs = log_content[start:end]

    # Custom pagination object or simple dict to pass to template
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_lines,
        'pages': (
            total_lines + per_page - 1) // per_page if total_lines > 0 else 1,
        'has_prev': page > 1,
        'has_next': end < total_lines,
        'prev_num': page - 1,
        'next_num': page + 1}

    return render_template('admin/logs.html',
                           title='System Logs',
                           logs=current_logs,
                           log_files=log_files,
                           selected_file=selected_file,
                           pagination=pagination,
                           current_level=level_filter,
                           current_q=keyword)


@bp.route('/logs/download/<path:filename>')
@admin_required
def download_log(filename):
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__))))
    log_dir = os.path.join(base_dir, 'logs')

    # Security check: ensure file exists and is within log_dir
    # send_from_directory handles directory traversal attacks but we should
    # double check
    if not os.path.exists(os.path.join(log_dir, filename)):
        abort(404)

    return send_from_directory(log_dir, filename, as_attachment=True)
