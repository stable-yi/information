from flask import current_app, jsonify
from flask import session
from . import index_blue
from flask import render_template

from info.utils.common import do_index_class

from info.utils.response_code import RET
from info.models import User,News,Category
from info  import constants
#  定义一个index视图
@index_blue.route("/")
def index():

    # 获取当前用户的id
    user_id = session.get("user_id")

    # 通过用户id查询等到用户的完整信息
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 获取新闻点击排行
    news_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)


    # 构建新闻列表的详细信息
    clicks_news_list = []
    for new in news_list:
        clicks_news_list.append(new.to_basic_dict())



    # 获取新闻分类的所有新闻
    categorys = Category.query.all()

    category_list  = []
    for category in categorys:
        category_list.append(category.to_dict())
    print(category_list)


    data = {
        "user_info": user.to_dict() if user else None,
        "click_news_list":clicks_news_list,
        "categorys":category_list
    }

    return render_template("news/index.html",data = data)


# 定义一个视图寻找favicon.ico静态图片
@index_blue.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")



