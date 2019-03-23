#! /usr/bin/env python
# coding:utf-8


"""news界面"""

from flask import Blueprint

news_blue = Blueprint("news",__name__,url_prefix="/news")

from . import views