from ._tcp import _ProtoType


class Listener(_ProtoType):
    def __init__(
            self, address, *, 
            listens:int|None=None, 
            timeout:float|None=None,
            settings:list[tuple]=[]
        ):
        super().__init__(address, listens=listens, timeout=timeout, settings=settings)
        
    def listen(self): # 启用TCP监听
        pass
    
    def _task(self):  # 注册监听任务
        pass
    
    def parse(self):  # 解析TCP数据包
        pass
    