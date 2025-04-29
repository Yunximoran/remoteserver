import json
import time
import socket
from typing import Dict, Tuple, AnyStr

from lib.database import Redis
from lib.manager import catch, Logger
from lib.sys.processing import Process
from lib.sys.sock.tcp import Listener
from lib import Resolver

database = Redis()
resolver = Resolver()
catch = catch(Logger("tcplisten", "tcplisten.log"))

ENCODING = resolver("global", "encoding")
RECVSIZE = resolver("sock", "recv-size")
DELAY = 1

class ListenServe(Listener):
    tasks: list[Process] = []
    @catch.timeout
    def accept(self):
        sock, addr = self.sock.accept()
        return sock, addr
    
    def listen(self):
        """
            TCP监听器
        监听来自客户端的TCP连接
        主要接受reports, 
        """
        tasks:list[Process] = []
        try:
            while True:
                # 接受客户端连接
                conn = self.accept()
                if not conn: continue
                print("hello")
                task = Process(target=self._task, args=conn)
                self.tasks.append(task)
                task.start()
        except KeyboardInterrupt:
          print("kill all tcp listen task")
          for task in self.tasks:
              task.terminate()
              task.join()
     
    def _task(self, sock:socket.socket, addr, data):
        # 任务包装器
        """
            解析连接对象
        """
        data = json.loads(sock.recv(RECVSIZE).decode(ENCODING))
        
        if data['label'] == "download":
            info = data['data']
            progress = json.loads(sock.recv(1024).decode(ENCODING))
            database.set(info['file'], progress['data'])
            database.expire(info['file'], 3)
        
    def _parse(self, data):
        """
            解析TCP数据
        返回 事件类型 和 Cookie
        """
        msg = json.loads(data)
        event_type = msg['type']
        cookie = msg['cookie']
        return event_type, cookie
    
    def _check_status(self, sock:socket.socket=None):
        try:
            sock.getpeername()
            return True
        except:
            return False
