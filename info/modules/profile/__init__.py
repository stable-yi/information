#! /usr/bin/env python
# coding:utf-8


"""个人中心"""
from flask import Blueprint


profile_blue = Blueprint("profile",__name__,url_prefix="/user")

from . import  views
