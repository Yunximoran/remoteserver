import json
import time
from typing import Dict

from lib.sys.processing import Process, Value
from lib.sys.sock.udp import BroadCastor as UDP
from lib import Resolver
from lib.sys import Logger
from static import DB


logger = Logger("udp", log_file="udp.log")
resolver = Resolver()

ENCODING = resolver("global", "encoding")
RECVSIZE = resolver("sock", "recv-size")
MAXTASKS = 10

class BroadCastor(UDP):
    """
    listen:
        启动监听
    
    task:
        注册每次接收到广播的任务
    """
    timers: Dict[str, Process] = {}  # 使用Manager共享字典
    
    def listen(self):   # 启用
        """
            注册监听任务
        """
        nowtasks = Value("i", 0, lock=True)
        logger.record(1, "UDP Listening")
        while True:
            if nowtasks.value < MAXTASKS:
                # 创建一个进程， task + 1
                task = Process(target=self._task, args=(nowtasks, ))
                task.start()

                # 原子操作：nowtasks.value += 1（自动锁保证安全）
                with nowtasks.get_lock():  # 显式获取锁确保复合操作安全
                    nowtasks.value += 1

    def _task(self, nowtasks):  # 创建监听任务
        # 接受广播数据
        # recvfrom 会阻塞进程，直到接收到数据
        try:
            # 接收心跳包广播
            data, address = self.sock.recvfrom(RECVSIZE)
            
            # 解析广播数据
            data, ip = self.parse(data, address)
            logger.record(1, f"conning for client: {ip}")
            # 保存/更新 广播数据
            self.update_client_messages(ip, data)
            
            # 启动计时器，检测客户端是否断开连接
            Process(target=self._timer, args=(ip, )).start()
        finally:
            with nowtasks.get_lock():
                nowtasks.value -= 1
    
    def parse(self, data:bytes, addr:str):  # 解析UDP数据包
        data = data.decode(ENCODING)
        ip = json.loads(data)['ip']
        return data, ip
    
    def update_client_messages(self, ip, data): # 更新客户端信息
        DB.hset("client_status", ip, "true")
        DB.hset("heart_packages", mapping={ip: data}) # ip地址和心跳包数据
    
        DB.set(ip, "null")
        DB.expire(ip, 3)
    
    def _timer(self, ip): # 创建计时器
        time.sleep(3)
        if not DB.get(ip) and DB.hget("client_status", ip) == "true":
            DB.hset("client_status", ip, "false")
            logger.record(1, f"The client Disconnected:{ip}")
        
