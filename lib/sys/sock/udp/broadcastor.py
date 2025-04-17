import socket

from ._udp import _ProtoType


class BroadCastor(_ProtoType):

    def settings(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
    def listen(self):   # 启用广播监听
        super().listen()

    def _task(self):    # 注册广播任务
        pass
    
    def parse(self):    # 解析UDP数据包
        pass
    
    