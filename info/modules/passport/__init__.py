#! /usr/bin/env python
# coding:utf-8

"""注册和登陆"""
from flask import Blueprint

passport_blue = Blueprint("passport",__name__,url_prefix="/passport")


from . import  views