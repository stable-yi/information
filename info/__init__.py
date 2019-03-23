#! /usr/bin/env python
# coding:utf-8

import redis
from flask import g
from flask import render_template
from flask_session import Session
from flask_wtf.csrf import CSRFProtect,generate_csrf
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler

from config import config
from info.utils.common import do_index_class,user_login_data


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

    # 定义请求钩子，在每次请求结束后返回csrf_token值
    @app.after_request
    def after_request(response):
        # 生成csrf_token
        csrf_token = generate_csrf()

        response.set_cookie("csrf_token",csrf_token)

        return response

    # 捕获所有的404错误界面

    @app.errorhandler(404)
    @user_login_data
    def page_not_found(error):
        user = g.user
        data = {"user_info": user.to_dict() if user else None}
        return render_template('news/404.html', data=data)




    # 将自定义的过滤器添加到app库里面
    app.add_template_filter(do_index_class,"index_class")

    # 注册蓝图index界面
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)

    # 注册蓝图passport界面
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)

    # 注册蓝图news界面
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)

    # 注册profile 界面
    from info.modules.profile import profile_blue
    app.register_blueprint(profile_blue)
    # 注册admin界面
    from info.modules.admin import admin_blue
    app.register_blueprint(admin_blue)

    return app



