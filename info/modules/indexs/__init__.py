from flask import  Blueprint


index_blue = Blueprint("index",__name__)


# 要在蓝图的下面导入
from . import views


