from flask import current_app
from . import index_blue
from flask import render_template


#  定义一个index视图
@index_blue.route("/")
def index():
    return render_template("news/index.html")


# 定义一个视图寻找favicon.ico静态图片

@index_blue.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")