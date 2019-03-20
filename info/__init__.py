import redis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

# 将msyql数据库和应用进行关联
db = SQLAlchemy()

# redis数据库的配置
redis_store = ""


def create_app(config_name):
    """
    更具出刚入的配置信息创建应用
    :param config_name: 配置名字
    :return: 返回创建的应用app
    """


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

    return app

