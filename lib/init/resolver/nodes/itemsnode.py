from __future__ import annotations

from ._node import ITEMSNODE, Element, NODE
from .exception import ChildExistError    

class ItemsNode(ITEMSNODE):
    def __init__(self, node:Element, parent:NODE):
        self.tag = node.tag
        self.__li = node.findall("li")
        self.data = [li.text for li in self.__li]
        super().__init__(
            self.tag,
            node=node,
            parent=parent,
            childs=self.data
        )
    
    def push(self, item, describe=None):
        self._addelement(item, describe)
        
    def pop(self, item):
        self._delelement(item)
        
    def _addelement(self,text, describe=None):
        if text in self.data:
            raise ChildExistError(f"{text} is existed")
        attrib = {}
        if describe:
            attrib['describe'] = describe
        self.data.append(text)
        return super()._addelement("li", text, attrib)
    
    def _delelement(self, item):
        node = self.getelement()
        if item in self.data:
            index = self.data.index(item)
            node.remove(self.__li.pop(index))
            return self.data.pop(index)
        raise ChildExistError(f"{item} is not a child")
    
    def __str__(self):
        return f"{self.tag}: {self.data}"

if __name__ == "__main__":
    from lib import Resolver
    
    with Resolver() as resolver:
        r = resolver.root
        print(type(r))
        sock = resolver("sock", 'udp', 'ip-broad')
        print(sock)