from .init.resolver import Resolver
from .manager import Manager
from .catch import *

CatchSock = _CatchSock
# CatchDataBase = _CatchDataBase
CatchProcess = _CatchProcess



"""
自定义包结构规范

__init__.py:
    执行一些模块初始化操作
    导出需要在外部使用的模块


_: 单下划线开头 只在despose中调用
__: 双下划线开头 只在所在目录中被调用
* 个别需要被外部使用的模块可以再__init__.py 中导出 _[__](xxx) as (xxx)

"""

# 导出常用处理工具
if __name__ == "__main__":
    pass