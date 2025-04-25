# ==============================================解析器错误
class REASOLVERERROR(Exception): ... 
class ChildExistError(REASOLVERERROR): ...      # 子节点存在错误


# ==============================================节点错误
class NODEERR(Exception): ...
class NodeExistError(NODEERR): ...              # 节点存在错误
class NodeSecurity(NODEERR): ...                # 节点安全错误
class PathExistsError(Exception): ...           # 路径存在错误
class PathTypeError(Exception): ...             # 路径类型错误