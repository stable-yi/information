from flask import Flask

# 创建flask项目
app = Flask(__name__)


#  定义一个index视图

@app.route("/index")
def index():
    return "index"


if __name__ == "__main__":
    app.run()
