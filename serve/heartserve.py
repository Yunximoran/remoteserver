import json
import time
from typing import Dict

from lib.sys.processing import Process, Value, Event
from lib.sys.sock.udp import BroadCastor as UDP
from lib import Resolver
from lib.manager import Logger
from lib.database import Redis


logger = Logger("udp", log_file="udp.log")
resolver = Resolver()

ENCODING = resolver("global", "encoding")
RECVSIZE = resolver("sock", "recv-size")
MAXTASKS = 10
database = Redis()

class HeartServe(UDP):
    """
    listen:
        启动监听
    
    task:
        注册每次接收到广播的任务
    """
    stop = Event()

    def listen(self):   # 启用
        """
            注册监听任务
        """
        nowtasks = Value("i", 0, lock=True)
        tasks: list[Process]= []
        logger.record(1, "UDP Listening")
        try:
            while not self.stop.is_set():
                if nowtasks.value < MAXTASKS:
                    # 创建一个进程， task + 1
                    task = Process(target=self._task, args=(nowtasks, ))
                    tasks.append(task)
                    task.start()
                    # 原子操作：nowtasks.value += 1（自动锁保证安全）
                    with nowtasks.get_lock(): nowtasks.value += 1
        except KeyboardInterrupt:
            print("kill all udp listen task")
            self.stop.set()
            for task in tasks:
                task.join()
            self.sock.close()
            database.close()
    
    def _task(self, nowtasks):  # 创建监听任务
        # 接受广播数据
        # recvfrom 会阻塞进程，直到接收到数据
        # 接收心跳包广播
        self.sock.settimeout(1)
        while not self.stop.is_set():
            try: data, address = self.sock.recvfrom(RECVSIZE)
            except TimeoutError: continue

            # 解析广播数据
            data, ip = self.parse(data, address)
            logger.record(1, f"conning for client: {ip}")

            # 保存/更新 广播数据
            self.update_client_messages(ip, data)
            
            # 启动计时器，检测客户端是否断开连接
            timer = Process(target=self._timer, args=(ip, ))
            timer.start()
        
        # 释放任务计数器
        with nowtasks.get_lock():nowtasks.value -= 1
                
    
    def parse(self, data:bytes, addr:str):  # 解析UDP数据包
        data = data.decode(ENCODING)
        ip = json.loads(data)['ip']
        return data, ip
    
    def update_client_messages(self, ip, data): # 更新客户端信息
        database.hset("client_status", ip, "true")
        database.hset("heart_packages", mapping={ip: data}) # ip地址和心跳包数据
        database.set(ip, "null")
        database.expire(ip, 3)
    
    def _timer(self, ip):
        start_time = time.time()
        while not self.stop.is_set() and (time.time() - start_time < 3):
            time.sleep(0.1)
            
        if not self.stop.is_set():
            if not database.get(ip) and database.hget("client_status", ip) == "true":
                database.hset("client_status", ip, "false")
        
