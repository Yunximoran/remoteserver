from __future__ import annotations
import re
from pathlib import Path
from typing import List, AnyStr, Any, Generator, Dict, Union, TypeVar
from xml.etree.ElementTree import Element, SubElement

try:
    from ..exception import *
    from ...strtool import pattern
except ImportError:
    from lib.init.exception import *
"""
    
"""
class _Node:
    # 类操作
    def __init__(self, tag, node:Element, 
                 parent: Node|PathNode,
                 childs: List[Node|PathNode],
                ):
        self.tag = tag
        self.parent = parent
        self.address = self.__set_address()
        
        self.__node = node
        self.__childs = childs  
        
        
        self.__level = len(self.address) - 1
        if 'describe' in node.attrib:
            self.setdescribe(node.attrib["describe"])
        
    def getelement(self) -> Element:
        # 获取原始Element
        return self.__node   
    
    def type(self):
        # 获取节点类型，[树节点、结构节点， 列表节点， 选项节点]
        if isinstance(self, Node):
            if self.data is None:
                return "tree"
            else:
                return "val"     
        elif isinstance(self, PathNode):
            return "struct"
        elif isinstance(self, ItemsNode):
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
        
    def search(self, *tags) -> Node|PathNode|ItemsNode:
        # 创建指针，只想当前节点
        current = self
        for tag in tags:
            # 遍历标签， 逐级定位到指定节点
            current = current._search(tag)
            # 如果为空，定位错误，返回None
            if not current:
                break
        return current

    def _search(self, tag) -> _Node:
        if self.tag == tag:
            return self
        elif self.type() in ['items', "val"]:
            return False
        else:
            for next in self.__childs:
                res = next._search(tag)
                if res:
                    return res
        return False
    
    def _setattrib(self, key, val):
        # 为当前元素设置属性，并同步Node属性
        self.__node.set(key, str(val))
    
    def _delattrib(self, key):
        # 删除当前元素的某个属性，并同步Node属性
        if key in self.__node.attrib.keys():
            del self.__node.attrib[key]
        else:
            raise KeyError(f"{self} not attribute {key}")
    
    def _addelement(self, tag, text="\n", attrib = {}, index:int=None, **extra) -> Node:
        # 如果子节点已存在，返回子节点
        # 创建新Element
        if isinstance(index, int):
            newelem = Element(tag, attrib, **extra)
            self.__node.insert(index, newelem)
        else:
            newelem = SubElement(self.__node, tag, attrib, **extra)
        # 设置默认文本， 没有设置会成为单标签文件报错
        newelem.text = text + "\t" * self.__level if text == "\n" else text

        return newelem

    def _delelement(self, node: Node):
        self.__node.remove(node.getelement())
        
    def __set_address(self):
        if self.parent:
            addr = self.parent.__set_address()
            addr.append(self.tag)
        else:
            return [self.tag]
        return addr
        
    @staticmethod
    def __set_default_context(text, level):
        # 设置默认文本
        return text + "\t" * level if text == "\n" else text  
          
    def __contains__(self, item):
        if isinstance(item, str):
            return item in [child.tag for child in self.__childs]
        else:
            return item in self.__childs

    def __iter__(self) -> Generator[Union[Node, PathNode], None, None]:
        for elem in self.__childs:
            yield elem
    

    
class Node(_Node):
    def __init__(self, node:Element, parent:Node = None):
        self.tag = node.tag         # 节点名
        self.attrib = node.attrib   # 节点包含属性
        


        # 设置节点数据 
        self.data = self.data = self.__retype(node.text) if node.text is not None else None

        # 设置私有属性
        self.__node = node              # 原始Element对象
        self.__size = 0                 # 子元素数量
        self.__childs:List[Node] = []   # 子元素列表
        
        # 设置节点描述
        if "describe" in node.attrib.keys():
            self.describe = node.attrib["describe"]
        else:
            self.describe = None    
                   
        super().__init__(
            self.tag,
            node,
            parent,
            self.__childs, 
            )
        

    def setdata(self, data):
        # 对数据进行转换并设置为data属性
        self.data = self.__retype(data)
    
    def settext(self, text):
        if self.type() == "val":
            node = self.getelement()
            node.text = str(text)
            self.setdata(node.text)
        else:
            raise "must be a val node to set text"
        
    def addchild(self, node):
        # 添加子元素
        # node = self._addelement(tag, text, attrib, **extra)
        self.__childs.append(node)
        self.__size += 1
        
    def addelement(self, tag, text="\n", attrib:Dict = {}, **extra) -> Node:
        # 如果子节点已存在，返回子节点
        fount = self.search(tag)
        if fount is not None and abs(fount.__level - self.__level) == 1:
            return fount
        
        # 创建新Element
        newelem = super()._addelement(tag, text="\n", attrib = {}, **extra)
        
        # 生成新Node， 绑定父Node为self, 如果attrib中包含struct属性，创建PathNode，并绑定父元素为self
        newnode = Node(newelem, self) if "struct" not in attrib else PathNode(newelem, self)
        
        # 绑定子Node为新Node
        self.__childs.append(newnode)
        
        # 返回新Node， 执行一些额外测操作，如设置文本，设置属性，修改标签名等
        return newnode
        
    def delelement(self, node: Node):
        # 从子元素中找到目标Node
        if node in self.__childs:
            # 删除相关引用
            self.__childs.remove(node)
            self.__node.remove(node.getelement())
        else:
            # 否则报错目标Node不是当前Node的子元素
            raise ValueError("node not in childs")
    
    def setattrib(self, key, val):
        return super()._setattrib(key, val)
    
    def delattrib(self, key):
        return super()._delattrib(key)
    
    def __retype(self, context: AnyStr) -> int|float|str:
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


# 特殊节点处理
class PathNode(_Node):
    """
        路径节点
    # attrib包含struct的Element节点为根目录
    从该节点开始解析目录结构
    dir标签表示：子目录 创建子节点
    li标签：表示子文件， 添加进self.files
    
    # 提供关于路径的处理操作
    """

    def __init__(self, node: Element, parent:Node|PathNode):
        """
        tag: 目录名称
        describe: 目录描述
        """
        # parent 必要参数，且必须为 Node 或 PathNode
        if not isinstance(parent, Node|PathNode):
            raise "path node must a Node or PathNode"
        
        self.parent = parent        # 绑定 父目录 [父节点]
        self.status = node.attrib["status"] if "status" in node.attrib else "default"
        if isinstance(self.parent, Node):
            self.tag = node.tag     # 目录名称
            self.describe = node.attrib['struct']   # 文件描述
            self.path = Path(self.__set_path_status()) 
        else:
            self.tag = node.attrib["name"]  # 目录名称
            self.describe = node.attrib["describe"] if "describe" in node.attrib else None
            self.path = parent.path.joinpath(self.__set_path_status())

        self.dirs: List[PathNode] =[]
        for dir in node.findall("dir"):
            child = PathNode(dir, self)
            self.dirs.append(child)
        
        # 添加子文件, 保存子文件节点
        self.files: Dict[AnyStr, Path] = {}
        self.__files: Dict[AnyStr, Element] = {}
        for li in node.findall("li"):
            file_path = self.path.joinpath(li.text)
            self.files[file_path.name] = file_path 
            self.__files[file_path.name] = li       

        super().__init__(
            self.tag,
            node, 
            parent,
            self.dirs, 
            )
        
    def __set_path_status(self):
        if self.status == "hidden":
            return f".{self.tag}"
        if self.status == "protect":
            return f"_{self.tag}"
        if self.status == "private":
            return f"__{self.tag}"
        return self.tag
    
    def bind(self, last:Path, *args):
        # 绑定实际路径
        if isinstance(last, Path):
            path = last.joinpath(*args)
        else:
            path = Path(last).joinpath(*args)
            
        if not path.exists():
            raise PathExistsError(f"{path} is not exists")
        if path.is_file():
            raise PathTypeError(f"{path} is not a dir")
        return path.joinpath(self.path)

    def clean(self):
        glob = self.path.glob("*")
        for child in glob:
            if child.name not in self.files and child.name not in self.dirs:
                if child.is_dir():
                    child.rmdir()
                else:
                    child.unlink()
                    
    def exists(self, iter=False):
        """
            判断路径是否存在
        """
        state = self.path.exists()
        if not state:
            return self.tag, state
        if iter:
            results = []
            for child in self:
                results.append((child.tag, child.exists(iter=True)))
            
            for file in self.files:
                results.append((file, self.files[file].exists()))
            return results
        else:
            return self.tag, state     
                
    def resetfilename(self, old_fn, new_fn):
        """
            设置文件名
        old_fn: 原名称
        new_fn: 新名称
        """
        if not self.__check_filename(new_fn):
            raise 
        if old_fn in self.__files:
            # 获取对应文件节点，重新赋值
            fp = self.__files[old_fn]
            fp.text = new_fn
            
            # 修该files and __files 中的引用
            self.__files[new_fn] = fp
            self.files[new_fn] = self.path.joinpath(new_fn)
            del self.__files[old_fn]
            del self.files[old_fn]
            
        else:
            raise KeyError(f"without this file, create it first: {old_fn}")
        
    def resetdirname(self, name):
        """
            设置目录名
        """
        node = self.getelement()
        if self.tag == name:
            return
        elif isinstance(self.parent, Node):
            node.tag = name
        elif isinstance(self.parent, PathNode):
            node.attrib['name'] = name
        else:
            raise "current node is not a PathNode"
        self.tag = name
        
    def touch(self, file=None, *, iter=False, parents=False):
        """
            创建文件
        file: 要创建的文件
        iter: 是否遍历字节点
        """
        if not file and not iter:
            raise "please input file name or set iter is true"
        if not parents and self.parent.exists():
            raise "parent path not exist"
        
        if iter:
            for child in self:
                child.touch(iter=iter, parents=parents)
                
            for file in self.files.values():
                file.touch(exist_ok=True)
        else:
            if file not in self.files:
                raise "file not in self"
            self.files[file].touch(parents=parents, exist_ok=True)
    
    def mkdir(self, iter=False):
        """
            创建目录
        """
        self.path.mkdir(exist_ok=True)
        if iter:
            for dir in self.dirs:
                dir.mkdir(iter=iter)
            

    
    def rmdir(self):
        """
            删除目录， 只能删除当前， 要删除目录必须找到对应节点
        """
        self.path.rmdir()
        
    def rmfile(self, fn):
        """
            删除文件， 只能删除当前节点的内容， 要删除文件必须找到所在节点
        """
        if fn not in self.__files:
            KeyError(f"without this file, create it first: {fn}")
        else:
            node = self.getelement()
            node.remove(self.__files[fn])
            del self.__files[fn]
            del self.files[fn]
    
    
    def addfiles(self, filename, describe:str=None):
        # 添加文件
        self._addelement("li", filename, describe=describe)
        
        # 获取节点路径
        newfile = self.path.joinpath(filename)

        # 绑定文件所在目录
        self.files[newfile.name] = newfile
    
    def addchild(self, dirname:str, describe:str=None):
        # 添加目录
        attrib = {
            "name": dirname
        }
        if describe:
            attrib["describe"] = describe
            
        dir = self._addelement("dir", dirname, describe=describe)  # 创建一个新的Element节点
        dirnode = PathNode(dir, self)
        self.dirs.append(dirnode)
        
    def _addelement(self, tag, text, describe=None):
        """
            添加元素节点
        PathNode中只能创建 li 和 dir 标签
        根节点只会在 Node中被创建
        """
        if tag not in ["dir", "li"]:
            raise "pathnode, must a dir or li"
        print(text in self.dirs)
        if text in self or text in self.files:
            print(f"dir or file: {text}")
            raise "dir or file is exist"
        
        # 设置节点描述
        attrib = {}
        if describe:
            attrib["describe"] = describe
        
        # 创建目录节点
        if tag == "dir":
            attrib['name'] = text
            return super()._addelement(tag, attrib=attrib, index=0)
        
        # 创建文件节点
        if tag == "li" and not self.__check_filename(text):
            raise "Invalid filename"
        else:
            return super()._addelement(tag, text, attrib=attrib)
    
    def _setattrib(self, describe):
        # 设置文件描述
        return super()._setattrib("describe", describe)
    
    def _delattrib(self):
        # 删除文件描述
        super()._delattrib("describe")
    
    @staticmethod
    def __check_filename(text):
        return re.match(r"^[^\\\/]+?\.[^\\\/]+$", text)
    
    def __str__(self):
        return f"Path: {self.tag}"
    
    def __getitem__(self, key):
        if key in self.files.keys():
            return self.files[key]
        else:
            raise "there is no such file in directory"
        

class ItemsNode(_Node):
    def __init__(self, node:Element, parent:Node):
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