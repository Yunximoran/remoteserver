import sys
from socket import socket
from socket import error as SockError
from functools import wraps

from ._catch import __CatchBase, Logger
from ._catch import LOGSPATH, LIBPATH


class _CatchSock(__CatchBase):
    log_path = LOGSPATH.bind(LIBPATH)
    logger = Logger(
        name="sock", 
        log_file="socket.log",
        log_path=log_path
    )    
    def sock(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                self.record(func)
                return func(*args, **kwargs)
            except SockError as e:
                self.record(func, e, 3)
                return False
            except KeyboardInterrupt:
                self.record(func, "rece interrupted", 3)
                return False
            except Exception:
                pass
        return wrapper
        
    def status(self, func):
        # 校验SOCK连接状态
        @wraps(func)
        def wrapper(sock:socket, *args, **kwargs):
            try:
                func(sock, *args, **kwargs)
                self.record(func)
                return True
            except SockError:
                self.record(func, "连接错误", 3)
                return False
        return wrapper