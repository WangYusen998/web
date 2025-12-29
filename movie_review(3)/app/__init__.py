from flask import Flask, render_template, request
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from config import Config
# 新增日志配置 - 动态拼接绝对路径（适配PythonAnywhere）
import os
import logging
from logging.handlers import RotatingFileHandler

# 步骤1：获取当前文件（app/__init__.py）的绝对路径
CURRENT_FILE = os.path.abspath(__file__)
# 步骤2：定位到项目根目录（movie_review(3)）
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_FILE))
# 步骤3：拼接日志目录和文件的绝对路径
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'admin.log')

# 步骤4：确保日志目录存在（不存在则创建）
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
    os.chmod(LOG_DIR, 0o755)  # 赋予写入权限

# 步骤5：配置日志（带滚动+中文支持）
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [ADMIN] %(message)s',
    handlers=[
        # 写入文件（绝对路径）
        RotatingFileHandler(
            LOG_FILE,
            maxBytes=10*1024*1024,  # 单个日志最大10MB
            backupCount=5,  # 保留5个备份
            encoding='utf-8'  # 支持中文日志
        ),
        # 同时输出到终端（方便调试）
        logging.StreamHandler()
    ],
    force=True  # 强制覆盖旧配置
)

# 测试日志（验证配置生效）
logging.info(f"日志配置初始化成功！路径：{LOG_FILE}")
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
