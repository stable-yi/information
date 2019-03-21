import redis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
import logging
from logging.handlers import RotatingFileHandler
# 将msyql数据库和应用进行关联
db = SQLAlchemy()

# redis数据库的配置
redis_store = ""


def setup_log(config_name):
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)




def create_app(config_name):
    """
    更具出刚入的配置信息创建应用
    :param config_name: 配置名字
    :return: 返回创建的应用app
    """
    # 开启日志功能
    setup_log(config_name)

    # 创建flask项目

    app = Flask(__name__)


    # 项目应用添加配置信息
    app.config.from_object(config[config_name])

    # 配置数据库
    db.init_app(app)


    global redis_store
    # redis数据库的配置
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)

    # 跨站请求验证
    CSRFProtect(app)

    # 设置session保存位置
    Session(app)

    # 注册蓝图
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)

    return app



