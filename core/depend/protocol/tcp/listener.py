import json
import time
from typing import Dict, Tuple, AnyStr

from core.depend.protocol.tcp._prototype import TCP, socket
from static import DB
from lib import CatchSock
from lib.sys.processing import Process, Value
from lib import Resolver

resolver = Resolver()
catch = CatchSock()

ENCODING = resolver("global", "encoding")
RECVSIZE = resolver("sock", "recv-size")
TIMEOUT = resolver("sock", "tcp", "timeout")
LISTENES = resolver("sock", "tcp", "listenes")
DELAY = 1

class Listener(TCP):
    def settings(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(TIMEOUT)
        self.sock.listen(LISTENES)
    
    @catch.timeout
    def accept(self):
        sock, addr = self.sock.accept()
        return sock, addr

    @catch.sock
    def recv(self) -> Dict[AnyStr, Tuple[socket.socket, AnyStr]]:
        conn = self.accept()
        if conn:
            sock, addr = conn
            data = sock.recv(RECVSIZE)
            return sock, addr, data.decode(ENCODING)
        return False
    
    def listen(self):
        """
            TCP监听器
        监听来自客户端的TCP连接
        主要接受reports, 
        """
        while True:
            # 接受客户端连接
            try:
                conn = self.recv()
                if conn:
                    sock, addr, data = conn
                    task = Process(target=self._task, args=(sock, addr, data ))
                    task.start()
            except KeyboardInterrupt:
                exit()
     
    def _task(self, sock:socket.socket, addr, data):
        # 任务包装器
        """
            解析连接对象
        """
        data = json.loads(data)
        
        if data['label'] == "download":
            info = data['data']
            progress = json.loads(sock.recv(1024).decode(ENCODING))
            DB.set(info['file'], progress['data'])
            DB.expire(info['file'], 3)
        
    def _parse(self, data):
        """
            解析TCP数据
        返回 事件类型 和 Cookie
        """
        msg = json.loads(data)
        event_type = msg['type']
        cookie = msg['cookie']
        return event_type, cookie
    
    @catch.status
    def _check_status(self, sock:socket.socket=None):
        try:
            sock.getpeername()
            return True
        except:
            return False
