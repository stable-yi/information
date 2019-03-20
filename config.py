"""项目的所有配置文件"""
import redis

# 定义配置类
class Config(object):
    """工程配置信息"""
    # 开启调试模式
    DEBUG = True

    # 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #redis数据库配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # 设置秘钥
    SCERET_KEY = "J3NzXl/htksvCIbDecosasePqmpm9rGmKD9/dYYUkuYmcPreoBTaiv1GWfxt7etT"

    # session配置
    # flask_session的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒
