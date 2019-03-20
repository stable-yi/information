from . import index_blue



#  定义一个index视图
@index_blue.route("/")
def index():
    return "index"