from __future__ import annotations

import re
from typing import (
    List,
    Dict,
    AnyStr
)

from ._node import NODE, Element, pattern
from .pathnode import PathNode
  
class Node(NODE):
    def __init__(self, node:Element, parent:Node = None):
        # 初始化节点
        self.tag = node.tag  
        self.data = self.__conversion(node.text) if node.text is not None else None
        self.__childs:List[Node] = []   # 子元素列表
                   
        super().__init__(
            self.tag,
            node,
            parent,
            self.__childs, 
            )
        
    def setdata(self, data):
        # 对数据进行转换并设置为data属性
        self.data = self.data
        if self.type() == "val":
            node = self.getelement()
            node.text = str(data)
        else:
            raise "must be a val node to set text"
        
    def create(self, tag, text="\n", attrib:Dict = {}, mode="*", **extra) -> Node:
        # 校验子节点中没有重复
        fount = self.search(tag)
        if fount is not None and abs(fount.__level - self.__level) == 1:
            return fount
        
        # 创建新Element
        newelem = super()._addelement(tag, text=text, attrib=attrib, **extra)
        
        # 生成新Node， 绑定父Node为self, 如果attrib中包含struct属性，创建PathNode，并绑定父元素为self
        newnode = Node(newelem, self) if "struct" not in attrib else PathNode(newelem, self)
        
        # 绑定子Node为新Node
        self._addchild(newnode)
        
        # 返回新Node， 执行一些额外测操作，如设置文本，设置属性，修改标签名等
        return newnode
        
    def delete(self, node: Node):
        # 从子元素中找到目标Node
        if node in self.__childs:
            # 删除相关引用
            self._delchild(node)
            super()._delelement(node)
        else:
            # 否则报错目标Node不是当前Node的子元素
            raise ValueError("node not in childs")

    
    def setattrib(self, key, val):
        return super()._setattrib(key, val)
    
    def delattrib(self, key):
        return super()._delattrib(key)
    
    def _addchild(self, node):
        self.__childs.append(node)

    def _delchild(self, node):
        self.__childs.remove(node)

    def __conversion(self, context: AnyStr) -> int|float|str:
        """
            对数据进行转换
        """
        if re.match(pattern.INT, context):
            return int(context)
        elif re.match(pattern.FLOAT, context):
            return float(context)
        elif re.match(pattern.IS_BOOL_TRUE, context):
            return True
        elif re.match(pattern.IS_BOOL_FALSE, context):
            return False
        elif re.match(pattern.IS_NONE, context):
            # 只有树节点self.data为空
            return None
        else:
            return context 
    
    
    def __str__(self) -> AnyStr:
        type = self.type()
        if type == "struct":
            return f"struct root: {self.tag}"
        if type == "list":
            return "\n".join(self.data)
        if type == "tree":
            return f"node: {self.tag}"
        return f"option {self.tag} :\t{self.data}"
    
    def __getitem__(self, key):
        """
            获取额外的属性数据
        """
        if key == "describe":
            raise "describe is default attribute, plcess get it from the cls"
        if key == "struct":
            raise "struct is safe attribute, plcess get it for the cls"
        return self.attrib[key]
    
    def __setitem__(self, key, val):
        pass