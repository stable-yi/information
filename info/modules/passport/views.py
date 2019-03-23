#! /usr/bin/env python
# coding:utf-8


import random
from datetime import datetime

from flask import current_app
from flask import make_response
from flask import request, jsonify
import re
from flask import redirect

from flask import session
from flask import url_for

from info.utils.response_code import RET
from . import passport_blue
from info.utils.captcha.captcha import captcha
from info import redis_store
from info import constants
from info.models import User
from info.utils.yuntongxun.sms import CCP
from info import db





@passport_blue.route("/image_code")
def get_image_code():
    """
    路由：/passport/image_code?image_code_id=uuid
    :return: image
    """
    # 获取图片image_code_id
    image_code_id = request.args.get("imageCodeId")

    if image_code_id is None:
        return jsonify(error=RET.PARAMERR,errmsg="参数错误")
    # 获取图片验证码
    name,text,image = captcha.generate_captcha()


    #将图片的验证码保存到redis数据中
    try:
        redis_store.setex("img_%s" % image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(error=RET.DBERR,errmsg="保存图片验证码失败"))

    resp = make_response(image)
    resp.headers['Content-Type'] = "image/jpg"

    return  resp


# URL：/passport/sms_code?mobile=xx&image_code=xx&image_code_id
# 请求方式：POST
# 传入参数：JSON格式
@passport_blue.route("/sms_code",methods=["GET","POST"])
def get_sms_code():
    """发送短信"""
    # 获取参数
    mobile = request.json.get("mobile")
    image_code = request.json.get("image_code")
    image_code_id = request.json.get("image_code_id")

    # 校验参数
    if not all([mobile,image_code_id,image_code]):
        # 参数不全
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")

    # 校验手机号
    if not re.match(r"^1[345678]\d{9}$",mobile):
        # 手机号错误
        return jsonify(error=RET.PARAMERR, errmsg="手机号错误")

    # 通过传入的图片id取出来图片验证码
    real_image_code = ""
    try:
        real_image_code = redis_store.get("img_%s" % image_code_id)
        # 如果能够取出来值，删除redis中缓存的内容
        if real_image_code:
            real_image_code = real_image_code.decode()
            redis_store.delete("img_%s" % image_code_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="获取图片验证码失败")

    # 图片验证码是否存在
    if not real_image_code:
        return jsonify(error=RET.DATAERR, errmsg="图片验证码已过期")

    # 校验图片验证码是否正确
    if image_code.lower() != real_image_code.lower():
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")

    # 校验手机号是否已经注册
    try:
        user = User.query.filter_by(mobile = mobile).first()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="数据库查询错误")

    if user:
        # 该手机号已经注册
        return jsonify(error=RET.DATAERR, errmsg="手机号已经注册")

    # 生成短息验证码
    sms_code = "{:06d}".format(random.randint(0,999999))

    current_app.logger.debug("短信验证码的内容:%s" % sms_code)

    timeout = constants.SMS_CODE_REDIS_EXPIRES // 60
    result = CCP().send_template_sms(mobile,[sms_code,timeout],constants.SMS_CODE_TEMPLATE)

    # if result != 0 :
    #     # 发送短信失败
    #     return jsonify(error=RET.THIRDERR, errmsg="发送短信失败")



    # redis中保存短息验证码
    try:
        redis_store.setex("sms_%s" % mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(error=RET.DBERR, errmsg="短信验证码保存失败"))


    # 返回操作成功
    return jsonify(errno=RET.OK,errmsg="发送成功")


@passport_blue.route("/register",methods = ["POST","GET"])
def register():
    """
    注册
    URL：/passport/register
    请求方式：POST
    传入参数：JSON格式
    mobile	string	是	手机号
    smscode	string	是	短信验证码
    password	string	是	密码
    返回类型：JSON
    参数名	类型	是否必须	参数说明
    errno	int	是	错误码
    errmsg	string	是	错误信息

    """

    # 第一步 获取参数
    mobile = request.json.get("mobile")
    smscode = request.json.get("smscode")
    password = request.json.get("password")


    # 校验参数是否存在
    if not all([mobile,password,smscode]):
        """参数错误"""
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")

    # 校验手机号
    if not re.match(r"^1[345678]\d{9}$", mobile):
        # 手机号错误
        return jsonify(error=RET.PARAMERR, errmsg="手机号错误")

        # 校验手机号是否已经注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="数据库查询错误")

    if user:
        # 该手机号已经注册
        return jsonify(error=RET.DATAERR, errmsg="手机号已经注册")

    # 通过传入的短息id取出来短息验证码
    real_sms_code = ""
    try:
        real_sms_code = redis_store.get("sms_%s" % mobile)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="获取短息验证码错误")


    if not real_sms_code:
        return jsonify(error=RET.NODATA, errmsg="短信验证码已过期")

    real_sms_code = real_sms_code.decode()

    if real_sms_code != smscode:
        return jsonify(error=RET.DATAERR, errmsg="短信验证码错误")

    try:
        redis_store.delete("sms_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)


    # 初始化用户
    try:
        user = User()
        user.nick_name = mobile
        user.mobile = mobile
        user.password = password

        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

        return jsonify(error=RET.DATAERR, errmsg="数据保存错误")

    # 保存用户登陆状态
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile


    return jsonify(errno = RET.OK,errmsg ="用户创建成功")




@passport_blue.route("/login",methods=["POST","GET"])
def login():
    """
    用户登陆
    :return: ok
    """

    # 获取参数
    mobile = request.json.get("mobile")
    password = request.json.get("password")

    # 校验参数
    if not all([mobile,password]):
        return jsonify(errno = RET.PARAMERR,errmsg = "请求参数错误")

    # 从数据库中查询出指定用户
    try:
        user = User.query.filter_by(mobile = mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询错误")

    if not user:
        return jsonify(errno = RET.DATAERR,errmsg = "该用户不存在")

    # 校验密码
    if not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg="密码错误")

    # 保存用户的登陆状态
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    # 记录用户的最后一次登陆时间
    user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)


    return jsonify(errno = RET.OK,errmsg = "OK")



@passport_blue.route("/logout")
def logout():
    """
    退出登陆
    :return: ok
    """

    # 删除session中值
    # 字典通过session.pop("",none)
    session.pop("nick_name",None)
    session.pop("mobile",None)
    session.pop("user_id",None)
    session.pop('is_admin', None)

    return redirect(url_for("admin.admin_login"))
    # return jsonify(errno=RET.OK, errmsg="OK")