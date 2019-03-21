from flask import current_app
from flask_migrate import MigrateCommand,Migrate
from flask_script import Manager
from info import create_app,db
from info import models


app = create_app("developement")

# manage管理注册
manager = Manager(app)

# 数据库迁移
Migrate(app,db)
manager.add_command("db",MigrateCommand)



if __name__ == "__main__":
    manager.run()
