from functools import wraps

from ._catch import __CatchBase, Logger
from ._catch import LOGSPATH, LIBPATH

DBLOGS = LOGSPATH.search("db")

class _CatchDataBase(__CatchBase):
    log_path = DBLOGS.bind(LIBPATH)
    mysql_logger = Logger(
        name="mysql logs",
        log_file="mysql.log",
        log_path=log_path
    )
    redis_logger = Logger(
        name="redis log",
        log_file="redis.log",
        log_path=log_path
    )
    
    def ping(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ConnectionError:
                return False
        return wrapper
        
    def redis(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                self.record(func, logger=self.redis_logger)
                return func(*args, **kwargs)
            except ConnectionError:
                self.record(func, "无法连接Redis", 3, logger=self.redis_logger)
                return False
        return wrapper

    def mysql(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                self.record(func, f"execute success {args[-1]}", logger=self.mysql_logger)
                return func(*args, **kwargs)
            except Exception as e:
                self.record(func, f"execute error {args[-1]}\n {e}", 3, logger=self.mysql_logger)
                return False
        return wrapper