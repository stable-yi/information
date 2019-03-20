import redis
from flask_wtf.csrf import CSRFProtect
from flask import Flask
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import MigrateCommand,Migrate
from flask_script import Manager


from config import Config


# 创建flask项目
app = Flask(__name__)


# 注册配置信息到工程中
app.config.from_object(Config)

# 将msyql数据库和应用进行关联
db = SQLAlchemy(app)

# 跨站请求验证
CSRFProtect(app)

# redis数据库的配置
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# manage管理注册
manager = Manager(app)

#  定义一个index视图
@app.route("/")
def index():
    return "index"


if __name__ == "__main__":
    manager.run()
