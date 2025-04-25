import os
import json
import re
from typing import List
from redis import StrictRedis

from lib.init.resolver import __resolver
from lib.strtool import pattern
from lib.catch import _CatchDataBase

catch = _CatchDataBase()


REDISCONF = __resolver("redis")
HOST = REDISCONF.search("host").data
PORT = REDISCONF.search("port").data
DB = REDISCONF.search("db").data
try:
    PASSWORD = REDISCONF.password
except Exception:
    PASSWORD = None

class Connector(StrictRedis):
    """
        Redis操作模块，只在redis服务启动后可用
    """
    def __init__(self):
        super().__init__(
            host=HOST,
            port=PORT, 
            password=PASSWORD, 
            db=DB, 
            decode_responses=True)
        
    @catch.ping
    def status(self):
        self.ping()
    
    
    def lrange(self, key, start = 0, end=None) -> list:
        if end is None:
            end = self.llen(key)
        return super().lrange(key, start, end)

    def save(self, **kwargs):
        return super().save(**kwargs)
        
    @catch.redis
    def execute_command(self, *args, **options):
        return super().execute_command(*args, **options)
    
    
    @catch.redis
    def dump(self,data):
        """
        
        """
        pass
    
    def loads(self, data):
        """
            读取redis数据, 转化为PYTHON对象
        """
    
        if isinstance(data, dict):
            results = {}
            for next in data:
                next_data = self.loads(data[next])
                results[next] = next_data
            return results
        if isinstance(data, list):
            results = []
            for next in data:
                next_data = self.loads(next)
                results.append(next_data)
            return results
        

        
        try:
            data = json.loads(data)
            return self.loads(data)
        except Exception:
            return data
    

Redis = Connector() 

if __name__ == "__main__":
    da = Redis.hgetall("classify")  
    a = Redis.loads(da)
    print(a)