
from typing import Tuple, Any, List
import subprocess
import socket
from serve import HeartServe, ListenServe
from lib.database import Redis
from lib.sys.processing import Process
from lib import Resolver

database = Redis()
resolver = Resolver()

# FASTAPI设置常量
FASTAPP = resolver("server", "app")
FASTHOST = resolver("server", "host")
FASTPORT = resolver("server", "port")
ISRELOAD = resolver("server", "reload")

TIMEOUT = resolver("sock", "tcp", "timeout")
LISTENES = resolver("sock", "tcp", "listenes")

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
        for ip in database.hgetall("client_status"):
            database.hset("client_status", ip, "false")

        subprocess.Popen("uvicorn {} --host {} --port {} {}".format(FASTAPP, FASTHOST, FASTPORT, "--reload" if ISRELOAD else None))

        self.__starttasks()
        self.__jointasks()


    @staticmethod
    def _tcplisten():
        # 启动TCP监听服务： 
        ListenServe(SERVERADDRESS,
            listens=LISTENES,
            timeout=TIMEOUT,
            settings= [
                (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            ]
            ).listen()

    @staticmethod
    def _udplisten():
        # 启动广播监听服务：
        HeartServe(BROADCAST_1).listen()
        
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
        try:
            for server in self.Tasks:
                server.join()
        except KeyboardInterrupt:
            for server in self.Tasks:
                server.terminate()
                server.join()
            self.__starttasks()

if __name__ == "__main__":
    Start()
