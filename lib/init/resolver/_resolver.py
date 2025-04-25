from pathlib import Path

from typing import List, AnyStr, ByteString
from xml.etree import ElementTree as et
from xml.etree.ElementTree import Element

from .nodes import Node, PathNode, ItemsNode
from .nodes.exception import *
    
WORKDIR = Path.cwd()
PRIVATECONF = WORKDIR.joinpath("lib", "init", ".config.xml")
PUBLICCONF = WORKDIR.joinpath("lib", ".config.project.xml")
ENCODING = "utf-8"

class _Resolver:
    def __init__(self, file=PRIVATECONF):
        self.__file = file
        self.__conf = et.parse(file)
        self.__root = self.__conf.getroot()
        self.root = self._deep(self.__root)
        
        
    def save(self):
        # 设置缩进
        et.indent(self.__conf, space="\t", level=0)
        # 写入修改
        self.__conf.write(self.__file, encoding=ENCODING)
        
    def _deep(self, root: Element, parent: Node = None) -> Node|PathNode|ItemsNode:
        """
            解析器
        返回字典数据
        node: 解析开始节点
        addr: 节点所在位置，如果为空列表则表示从根节点开始
        """
        # 创建节点
        node = Node(root, parent)
        # 解析路径配置
        if "struct" in root.attrib:
            return PathNode(root, parent)
        
        # 解析集合配置
        elif "items" in root.attrib:
            return ItemsNode(root, parent)
        
        else:
            # 遍历子元素，创建Node绑定父节点为当前节点
            for elem in root:
                next = self._deep(elem, parent=node)
                node._addchild(next)
        return node   
    
    def tohtml(self, node:Element) -> AnyStr:
        # 获取配置文件原始文档
        return et.tostring(node)   
    
    def __call__(self, *args, is_node=False) -> Node|PathNode|ItemsNode|AnyStr:
        node = self.root.search(*args)
        if node is None:
            setpath = " - ".join(args)
            raise NodeExistError(f"Setting not Exist: {setpath}")
        else:
            if node.type() in ["struct", "tree", "items"] or is_node:
                return node
            return node.data
    
    def __iter__(self):
        if self.root:
            return self.root.__iter__()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *_):
        self.save()

__all__ = [
    "PRIVATECONF",
    "PUBLICCONF",

    "_Resolver"
]
    