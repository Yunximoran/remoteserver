import multiprocessing
from functools import partial
from multiprocessing import Process as _Process
from multiprocessing.pool import Pool as _Pool
from multiprocessing import (
    Lock,
    Queue,
    Value,
)

from lib.init.resolver import __resolver
from lib.catch import _CatchProcess


catch = _CatchProcess()
MINPROCESSES = __resolver("preformance", "min-processes") 
MAXPROCESSES = __resolver("preformance", "max-processes")

@catch.process
def worker(target, *args, **kwargs):
    """
        包装工作函数
    func: 目标函数
    args: 函数实参元组
    kwargs: 函数实参字典
    """
    return target

# 获取进程输出信息
def stdout(res):
    print(res)
    
# 获取进程错误信息
def stderr(err):
    print(err)


class Pool(_Pool):
    
    def __init__(self, processes = None, initializer = None, initargs = (), maxtasksperchild = None, context = None):
        """
            初始化进程池
        定义进程数范围
        """
        if processes is None or processes < 5:
            processes = MINPROCESSES 
        elif processes > 10:
            processes = MAXPROCESSES
        super().__init__(processes, initializer, initargs, maxtasksperchild, context)
        
    def map_async(self, func, iterable, *, attribute={}, chunksize = None, callback = None, error_callback = None):
        # 包装工作函数， 添加多进程异常捕获， 设置特定情况下函数缺失属性
        _worker = partial(worker, func, attribute=attribute)
        return super().map_async(_worker, iterable, chunksize, callback, error_callback)

    def apply_async(self, func, args=(), kwds={}, *, attribute={}, callback=None, error_callback=None):
        _worker = partial(worker, func, attribute=attribute)
        return super().apply_async(_worker, args, kwds, callback, error_callback)

    @catch.process
    def join(self):
        return super().join()

    

class Process(_Process):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, attribute={}, daemon = None):
        super().__init__(group, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self._target = partial(worker, target, attribute=attribute)
    
    def start(self):
        return super().start()
    
    def run(self):
        return super().run()
    
    def join(self, timeout = None):
        try:
            return super().join(timeout) 
        except KeyboardInterrupt:
            self.terminate()