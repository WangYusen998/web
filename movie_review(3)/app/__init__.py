from flask import Flask, render_template, request
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'main.login'
limiter = Limiter(key_func=get_remote_address)
csrf = CSRFProtect()


def create_app(config_class=Config):
    # Initialize Flask app, pointing static folder to the sibling directory
    app = Flask(__name__, static_folder='../static')
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    # 导入models以注册user_loader
    from app import models
    models

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.admin import bp as admin_blueprint
    from app.admin import routes as admin_routes
    admin_routes
    app.register_blueprint(admin_blueprint)

    # Initialize logging
    from app.logger import error_logger

    register_error_handlers(app, error_logger)

    return app


def register_error_handlers(app, error_logger):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        error_logger.error(
            '服务器错误: %s, URL: %s, IP: %s',
            error,
            request.url,
            request.remote_addr
        )
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        # Pass through HTTP errors that are not 500 (like 403, 404 if not
        # caught above)
        if isinstance(error, HTTPException):
            return error

        error_logger.exception(
            '未捕获异常: %s, URL: %s, IP: %s',
            error,
            request.url,
            request.remote_addr
        )
        return render_template('errors/500.html'), 500
