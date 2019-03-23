# 自定义过滤器用于点击排行
import functools

from flask import current_app
from flask import g
from flask import session




def do_index_class(index):
    """
    返回样式class
    :param index: 传入的序列号
    :return: class
    """
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""


def user_login_data(func):
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        user_id = session.get("user_id",None)

        user=None
        if user_id:
            try:
                from info.models import User
                user  = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        g.user = user
        return func(*args,**kwargs)
    return wrapper