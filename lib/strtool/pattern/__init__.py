from .net import *
from .math import *
from .path import *

# 配置操作系统名称
TAG_OS = r"^(Windows)$|^(Linux)$|^(MacOS)$"


# 匹配bool值 和 None 值
IS_BOOL_TRUE = r"^(1){1}$|^(true)$|^(yes)$"
IS_BOOL_FALSE = r"^(0){1}$|^(false)$|^(no)$"
IS_NONE = r"^(\s*)$"


ENCODE_BASE64 = r'^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$'