#! /usr/bin/env python3
# coding:utf-8


from flask import abort
from flask import current_app, jsonify
from flask import g
from flask import request
from . import index_blue
from flask import render_template

from info.utils.response_code import RET
from info.models import User,News,Category
from info  import constants
from info.utils.common import user_login_data

#  定义一个index视图
@index_blue.route("/")
@user_login_data
def index():

    # # 获取当前用户的id
    # user_id = session.get("user_id")
    #
    # # 通过用户id查询等到用户的完整信息
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 获取新闻点击排行
    news_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # abort(404)
    # 构建新闻列表的详细信息
    clicks_news_list = []
    for new in news_list:
        clicks_news_list.append(new.to_basic_dict())



    # 获取新闻分类的所有新闻
    categorys = Category.query.all()

    category_list  = []
    for category in categorys:
        category_list.append(category.to_dict())


    data = {
        "user_info": g.user.to_dict() if g.user else None,
        "click_news_list":clicks_news_list,
        "categorys":category_list
    }

    return render_template("news/index.html",data = data)


# 定义一个视图寻找favicon.ico静态图片
@index_blue.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")



# 新闻列表
@index_blue.route("/newslist")
def get_news_list():
    """
    获取新闻列表
    :return:
    """

    # 获取参数
    category_id = request.args.get("category_id",1)
    page = request.args.get("page",1)
    page_size = request.args.get("page_size",constants.HOME_PAGE_MAX_NEWS)

    # 参数校验
    try:
        page = int(page)
        page_size=int(page_size)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.PARAMERR,errmsg="参数错误")

    # 查询数据并且分页，cid=1从总新闻列表查找
    if not category_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    filter = [News.status == 0]
    if category_id != '1':
        filter.append(News.category_id==category_id)
    print(*filter)

    try:
        paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(page,page_size,False)

        news_itmes = paginate.items  # 获取所有的新闻信息
        current_page = paginate.page # 获取当前页面
        total_page = paginate.pages # 获取总共多少页
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败")

    news_list = []
    for news in news_itmes:
        news_list.append(news.to_basic_dict())


    return  jsonify(errno = RET.OK,errmsg = "OK",current_page = current_page,
                    total_page=total_page,news_list=news_list)