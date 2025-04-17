import socket

RECVSIZE = 1024
ENCODING = "utf-8"

class _ProtoType:
    def __init__(self, cast=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.settings()
        if cast:
            # 接收的时候才需要绑定地址
            self.sock.bind(cast)
            
    def listen(self):
        while True:
            self.recv()
    
    def settings(self):
        pass
    
    def recv(self):
        data, addr = self.sock.recvfrom(RECVSIZE)
        return data.decode(ENCODING), addr
    
    def send(self, data:str, cast:tuple):
        self.sock.sendto(data.encode(ENCODING), cast)