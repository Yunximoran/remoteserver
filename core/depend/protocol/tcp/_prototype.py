import socket



class TCP:
    def __init__(self, address=None):
        # 创建TCP套接字对象
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 初始化TCP套接字
        
        if address:
            self.sock.bind(address)
            
        # SOCK设置选项
        self.settings() 
        
    
    def settings(self):
        pass
