import socket
import json
import time

RECVSIZE = 1024
ENCODING = "utf-8"

class _ProtoType:
    def __init__(
            self, address, *, 
            listens:int|None=None,
            timeout:float|None=None,
            settings:list[tuple]=None
        ):
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.settings(settings)
        
        self.sock.bind(address)
        if listens:
            self.sock.listen(listens)
            
        self.sock.settimeout(timeout)
        
    
    def cform(self, label, data): # 创建表单
        return json.dumps({
            "label": label,
            "data":data,
            "ctime": time.time()
        }, ensure_ascii=False, indent=4).encode(ENCODING)
    
    def settings(self, settings):
        for option in settings:
            self.sock.setsockopt(*option)
            
    
    def send(self, data:str):
        if not isinstance(data, bytes):
            data = data.encode(ENCODING)
        self.sock.sendall(data)
    
    def recv(self):
        data = self.sock.recv(RECVSIZE)
        return data.decode(ENCODING)    
    
    def accept(self):
        return self.sock.accept()
    
    def close(self):
        self.sock.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *_):
        self.close()
    