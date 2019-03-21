# 自定义过滤器用于点击排行


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