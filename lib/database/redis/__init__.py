import json

from .connector import Connector


class WorkBench:
    def __init__(self, conn:Connector):
        self.conn = conn
        
    def check(self, data):
        pass
    
    def dump(self):
        pass
    
    def load(self):
        pass
    
    def addtb(self):
        pass
    
    def deltb(self):
        pass