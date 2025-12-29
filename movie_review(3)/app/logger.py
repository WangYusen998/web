import logging
import os
from logging.handlers import TimedRotatingFileHandler
from flask import request

# 日志文件夹
LOG_DIR = 'logs'


def setup_logger(name, log_file, level=logging.INFO):
    """创建并配置一个logger"""

    # 确保日志目录存在
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # 日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件处理器（按天分割）
    file_handler = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, log_file),
        when='midnight',
        interval=1,
        backupCount=30,  # 保留30天
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 创建各个专用logger
auth_logger = setup_logger('AUTH', 'auth.log')
db_logger = setup_logger('DB', 'database.log')
admin_logger = setup_logger('ADMIN', 'admin.log')
error_logger = setup_logger('ERROR', 'error.log', level=logging.ERROR)

# 便捷函数


def log_db(
        action,
        model_type,
        record_id=None,
        name=None,
        operator=None,
        details=None):
    """
    记录数据库操作日志
    :param action: 'add', 'edit', 'delete', 'batch_delete', 'enable', 'disable'
    :param model_type: 'movie', 'review', 'user', 'favorite'
    :param record_id: 记录ID
    :param name: 记录名称（如电影标题、用户名）
    :param operator: 操作者对象（通常是 current_user）
    :param details: 其他详细信息（字典或字符串）
    """
    try:
        ip = request.remote_addr
    except BaseException:
        ip = 'unknown'

    action_map = {
        'add': '添加', 'edit': '编辑', 'delete': '删除',
        'batch_delete': '删除 (批量)', 'enable': '启用', 'disable': '禁用'
    }
    model_map = {
        'movie': '电影', 'review': '评论', 'user': '用户', 'favorite': '收藏'
    }

    act_str = action_map.get(action, action)
    model_str = model_map.get(model_type, model_type)

    # 确定日志级别
    if action in ['delete', 'batch_delete', 'disable']:
        log_func = db_logger.warning
    else:
        log_func = db_logger.info

    info_parts = []

    # 构建信息部分
    if record_id:
        if model_type == 'review' and action == 'batch_delete':
            info_parts.append(f"评论ID:{record_id}")
        else:
            info_parts.append(f"ID:{record_id}")

    if name:
        if model_type == 'user':
            info_parts.append(f"目标用户:{name}")
        elif model_type == 'review' or model_type == 'favorite':
            info_parts.append(f"电影:{name}")
        else:
            info_parts.append(f"标题:{name}")

    if operator:
        # 对于普通用户操作（评论、收藏），显示“用户:xxx”
        # 对于管理操作，显示“操作者:xxx”
        if model_type in ['review', 'favorite']:
            info_parts.append(f"用户:{getattr(operator, 'username', 'Unknown')}")
        else:
            operator_name = getattr(operator, 'username', 'Unknown')
            info_parts.append(f"操作者:{operator_name}")

    if details:
        if isinstance(details, dict):
            for k, v in details.items():
                info_parts.append(f"{k}:{v}")
        else:
            info_parts.append(str(details))

    info_parts.append(f"IP:{ip}")

    msg = f"[DB] {model_str}{act_str} - {', '.join(info_parts)}"
    log_func(msg)


def log_auth(action, user=None, email=None, success=True, reason=None):
    """
    记录认证相关日志
    :param action: 'register', 'login', 'logout'
    :param user: 用户对象
    :param email: 邮箱（用于登录失败/注册失败）
    :param success: 是否成功
    :param reason: 失败原因
    """
    try:
        ip = request.remote_addr
    except BaseException:
        ip = 'unknown'

    action_map = {
        'register': '新用户注册' if success else '注册失败',
        'login': '用户登录成功' if success else '登录失败',
        'logout': '用户登出'
    }

    act_str = action_map.get(action, action)

    info_parts = []

    if user:
        info_parts.append(f"用户名:{user.username}")
        if action == 'register':
            info_parts.append(f"邮箱:{user.email}")
    elif email:
        info_parts.append(f"邮箱:{email}")

    if reason:
        info_parts.append(f"原因:{reason}")

    info_parts.append(f"IP:{ip}")

    msg = f"[AUTH] {act_str} - {', '.join(info_parts)}"

    if success:
        auth_logger.info(msg)
    else:
        auth_logger.warning(msg)


def log_admin(action, admin_user, details=None):
    """
    记录管理员操作日志
    :param action: 操作动作描述
    :param admin_user: 管理员用户对象
    :param details: 详细信息
    """
    try:
        ip = request.remote_addr
    except BaseException:
        ip = 'unknown'

    info_parts = []
    info_parts.append(f"管理员:{getattr(admin_user, 'username', 'Unknown')}")

    if details:
        info_parts.append(str(details))

    info_parts.append(f"IP:{ip}")

    msg = f"[ADMIN] {action} - {', '.join(info_parts)}"

    # 如果是失败或删除类操作，使用WARNING
    if '失败' in action or '删除' in action:
        admin_logger.warning(msg)
    else:
        admin_logger.info(msg)
