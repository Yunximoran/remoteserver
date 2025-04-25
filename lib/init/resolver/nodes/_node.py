from __future__ import annotations
import base64, re
from typing import List, Generator, Union
from xml.etree.ElementTree import Element, SubElement

from .exception import *
from ....strtool import pattern

class _Node:
    # 类操作
    def __init__(self, tag, node:Element, 
                 parent: NODE|PATHNODE,
                 childs: List[NODE|PATHNODE],
                ):
        self.tag = tag
        self.parent = parent
        self.address = self.__set_address()
        
        self.__node = node
        self.__childs = childs
        self.__attrib = node.attrib  
        
        
        self.__level = len(self.address) - 1
        if 'describe' in node.attrib:
            self.describe = node.attrib['describe']

        if "password" in node.attrib:
            passwd = node.attrib['password']
            if re.fullmatch(pattern.ENCODE_BASE64, passwd[2:-1]):
                self.password = base64.b64decode(passwd[2:-1]).decode()
            else:
                self._setattrib("password", passwd)
        else: self.describe = None
        
    def getelement(self) -> Element:
        # 获取原始Element
        return self.__node   
    
    def type(self):
        # 获取节点类型，[树节点、结构节点， 列表节点， 选项节点]
        if isinstance(self, NODE):
            if self.data is None:
                return "tree"
            else:
                return "val"     
        elif isinstance(self, PATHNODE):
            return "struct"
        elif isinstance(self, ITEMSNODE):
            return "items"
        else:
            raise f"type node error, {self}"
        
    def setdescribe(self, describe=None):
        self.describe = describe
        if describe:
            self._setattrib("describe", describe)
        
    def deldescribe(self):
        if self.describe:
            self._delattrib("describe")
        
    def search(self, *tags) -> NODE|PATHNODE|ITEMSNODE:
        # 创建指针，只想当前节点
        current = self
        for tag in tags:
            # 遍历标签， 逐级定位到指定节点
            current = current._search(tag)
            if current is None:
                break
            # 如果为空，定位错误，返回None
        return current

    def _search(self, tag) -> _Node:
        if self.tag == tag:
            return self
                
        if self.type() in ("tree", "struct"):
            for next in self.__childs:
                node = next._search(tag)
                if node is not None:
                    return node
        return None
    
    def _setattrib(self, key, val, elem:Element=None):
        # 为当前元素设置属性，并同步Node属性
        val = str(val)
        if key == "password":
            val = base64.b64encode(val.encode())
            
        if elem is None: self.__node.set(key, str(val))
        else: elem.set(key, str(val))

    def _delattrib(self, key, elem:Element=None):
        # 删除当前元素的某个属性，并同步Node属性
        if key in self.__node.attrib.keys():
            if elem is None: del self.__node.attrib[key]
            else: del elem.attrib[key]
        else:
            raise KeyError(f"{self} not attribute {key}")
        
    
    def _addelement(self, tag, text="\n", attrib:dict = {}, index:int=-1, **extra) -> NODE:
        # 创建新Element
        newelem = Element(tag)
        self.__node.insert(index, newelem)
        
        # 格式化缩进
        newelem.text = text + "\t" * self.__level if text == "\n" else text

        # 设置标签属性
        for option, val in attrib.items():
            self._setattrib(option, val, newelem)
        return newelem

    def _delelement(self, node: NODE):
        self.__node.remove(node.getelement())
        
    def __set_address(self):
        if self.parent:
            addr = self.parent.__set_address()
            addr.append(self.tag)
        else:
            return [self.tag]
        return addr
          
    def __contains__(self, item):
        if isinstance(item, str):
            return item in [child.tag for child in self.__childs]
        else:
            return item in self.__childs

    def __iter__(self) -> Generator[Union[NODE, PATHNODE], None, None]:
        for next in self.__childs:
            yield next

    def __len__(self):
        return len(self.__childs)
    
    def __getitem__(self, key):
        """
            获取额外的属性数据
        """
        if key == "describe":
            raise "describe is default attribute, plcess get it from the cls"
        if key == "struct":
            raise "struct is safe attribute, plcess get it for the cls"
        
        if key == "password":
            raise "password is safe attribute, plcess get it for the cls"
        
        return self.__attrib[key]
    
    def __setitem__(self, key, val):
        self._setattrib(key, val)

    def __delitem__(self, key):
        self._delattrib(key)
    

class NODE(_Node):
    pass

class PATHNODE(_Node):
    pass

class ITEMSNODE(_Node):
    pass

__all__ = [
    "Element",
    "SubElement",
    "NODE",
    "PATHNODE",
    "ITEMSNODE",
    "pattern"
]