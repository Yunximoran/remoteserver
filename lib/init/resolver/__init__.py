from ._resolver import *

# 公共解析器
def Resolver(file=PUBLICCONF):
    return _Resolver(file)

# 私有解析器
__resolver = _Resolver(PRIVATECONF)