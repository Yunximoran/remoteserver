from functools import wraps

from ._catch import __CatchBase, Logger
from ._catch import LOGSPATH, LIBPATH



class _CatchProcess(__CatchBase):
    log_path = LOGSPATH.bind(LIBPATH)
    logger = Logger(
        name="process",
        log_file="process.log",
        log_path=log_path
    )
    
    def pool(self):
        def decorator(func):
            @wraps(func)
            def wrapper(target, *args, **kwargs):
                pass
            return wrapper
        return decorator
    
    def process(self, func):
        @wraps(func)
        def wrapper(target, *args, **kwargs):
            if "attribute" in kwargs:
                attribute: dict = kwargs['attribute']
                for opt, val in attribute.items():
                    setattr(target, opt, val)
                del kwargs['attribute']
            try:
                self.record(target)
                return target(*args, **kwargs)
            except KeyboardInterrupt:
                self.record(target, "The Ctrl C", 3)
                return False
        return wrapper
    
    
    
    

