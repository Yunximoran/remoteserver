import sys
import signal

from typing import Tuple, Any, List
import uvicorn

from core.depend.protocol.tcp import Listener
from core.depend.protocol.udp import BroadCastor

from lib.sys.processing import Process, multiprocessing
from lib import Resolver

resolver = Resolver()

# FASTAPI设置常量
FASTAPP = resolver("server", "app")
FASTHOST = resolver("server", "host")
FASTPORT = resolver("server", "port")
ISRELOAD = resolver("server", "reload")

# 监听设置
SERVERADDRESS =(resolver("network", "ip"), resolver("ports", "tcp", "server"))
BROADCAST_1 = ("0.0.0.0", resolver("ports", "udp", "broad"))

class Start:
    Tasks: List[Process] = []
    def __init__(self) -> None:
        self.__registry((
            self._tcplisten,
            self._udplisten,
        ))
        
        self.__starttasks()
        uvicorn.run(app=FASTAPP, host=FASTHOST, port=FASTPORT, reload=ISRELOAD)
        self.__jointasks()
    
    @staticmethod
    def _tcplisten():
        # 启动TCP监听服务：
        Listener(SERVERADDRESS).listen()
    
    @staticmethod
    def _udplisten():
        # 启动广播监听服务：
        BroadCastor(BROADCAST_1).listen()
        
    # 注册服务
    def __registry(self, tasks: Tuple[Any]):
        # 注册依赖任务 
        for task in tasks:
            self.Tasks.append(Process(target=task))

    # 启动服务
    def __starttasks(self):
        for server in self.Tasks:
            server.start()
            
    # 等待服务
    def __jointasks(self):
        for server in self.Tasks:
            server.join()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    Start()
