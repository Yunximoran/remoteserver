import struct
import socket

from ._udp import _ProtoType


MULTICASTADDR = None    # 组播地址
RECVSIZE = 1024         # 
TTL = 1                 # 组播TTL

class MultiCastor(_ProtoType):
    def __init__(self):
        super().__init__()
        
    def listen(self):   # 启用广播监听
        pass
    
    def _task(self):    # 注册广播任务
        pass
    
    def parse(self):    # 解析UDP数据包
        pass
    
    def recv(self):
        self.join_multi_group("")
        self.sock.recv(RECVSIZE)
        
    
    def send(self, data:str, cast:tuple):
        self.set_ttl(1)
    
    def join_multi_group(self, multiaddr):
        group = socket.inet_ation(multiaddr)
        merq = struct.pack("4sL", group, socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, merq)
    
    def set_ttl(self):
        ttl = struct.pack("b", TTL)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)