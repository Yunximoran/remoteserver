from __future__ import annotations

import re
from pathlib import Path
from typing import (
    List,
    Dict,
    AnyStr
)

from ._node import *
from .exception import PathExistsError, PathTypeError

# 特殊节点处理
class PathNode(PATHNODE):
    """
        路径节点
    # attrib包含struct的Element节点为根目录
    从该节点开始解析目录结构
    dir标签表示：子目录 创建子节点
    li标签：表示子文件， 添加进self.files
    
    # 提供关于路径的处理操作
    """

    def __init__(self, node: Element, parent:NODE|PATHNODE):
        """
        tag: 目录名称
        describe: 目录描述
        """
        if not isinstance(parent, NODE|PATHNODE):
            raise "path node must a Node or PathNode"
        
        self.parent = parent        # 绑定 父目录 [父节点]
        self.status = node.attrib["status"] if "status" in node.attrib else "default"
        if isinstance(self.parent, NODE):
            self.tag = node.tag     # 目录名称
            self.describe = node.attrib['struct']   # 文件描述
            self.path = Path(self.__set_path_status()) 
        else:
            self.tag = node.attrib["name"]  # 目录名称
            self.describe = node.attrib["describe"] if "describe" in node.attrib else None
            self.path = parent.path.joinpath(self.__set_path_status())

        self.dirs: List[PATHNODE] =[]
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
        elif isinstance(self.parent, NODE):
            node.tag = name
        elif isinstance(self.parent, PATHNODE):
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
        
    def unlink(self, fn):
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
    
    
    def addfiles(self, filename, default=None, describe:str=None):
        # 添加文件
        if filename in self.files:
            raise FileExistsError(f"the {filename} file is exists")

        if not self.__check_filename(filename):
            raise "Invalid filename"
        
        super()._addelement("li", filename, {
            "default": default,     # 默认文本
            "describe": describe    # 文件描述
        })

        # 获取节点路径
        newfile = self.path.joinpath(filename)
        # 绑定文件所在目录
        self.files[newfile.name] = newfile
    
    def addchild(self, dirname:str, describe:str=None):
        if dirname in self:
            raise PathExistsError(f"the {dirname} directory is exists")
        
        # 添加目录
        attrib = {
            "name": dirname
        }
        if describe:
            attrib["describe"] = describe
        dir = super()._addelement("dir", dirname, {
            "name": dirname,
            "describe": describe
        }, index=0)  # 创建一个新的Element节点

        dirnode = PathNode(dir, self)
        self.dirs.append(dirnode)
        
        
    def _addelement_back(self, tag, text, describe=None):
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
        return re.match(pattern.FILENAME, text)
    
    def __str__(self):
        return f"Path: {self.tag}"
    
    def __getitem__(self, key):
        if key in self.files.keys():
            return self.files[key]
        else:
            raise "there is no such file in directory"
        

    def __len__(self):
        return len(self.dirs)