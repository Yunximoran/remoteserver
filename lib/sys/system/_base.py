import os
import time
import subprocess
import platform
import socket
import uuid
import re
import inspect
import sys
import ctypes
import json
import string
import zipfile,tarfile
from typing import List
from pathlib import Path
from collections.abc import Iterable
from xml.etree import ElementTree as et
from typing import Tuple
import psutil
from typing import Generator
from psutil import NoSuchProcess, AccessDenied

from ...manager import Logger


class Process:
    def __init__(self, process:psutil.Process):
        self.name = process.name().lower()
        self.pid = process.pid
        try:
            self.exe = process.exe()
        except (NoSuchProcess, AccessDenied):
            self.exe = None

class __BaseSystem:
    # 获取工作目录
    CWDIR = Path.cwd()
    _disks = []
    
    logger = Logger("system", "executor.log")
    def __init__(self):
        pass
    
    def _check_soft_status(self, path, *, pid=None) -> List[psutil.Process]:
        # 遍历系统进程池
        path = self._path(path)
        processes = []
        for process in psutil.process_iter():
            # 匹配项目
            try:
                curpath = Path(process.exe())
                item = Process(process)
                if re.match(path.stem, item.name):
                    # 进程路径包含 软件名
                    exe_depend_path = [Process(parent).exe for parent in process.parents()]
                    exe_depend_path.append(item.exe)
                    if str(path) in exe_depend_path:
                        processes.append(process)
                        continue
                if path.parent in curpath.parents:
                    # 需要区别单文件可执行程序
                    processes.append(process)
                    continue
            except psutil.AccessDenied:
                # 权限异常
                pass
            except psutil.NoSuchProcess:
                # 找不到进程
                pass
        return processes
    
    def _path(self, path:str|Path, *,
              check=False
              ) -> Path: # 路径转换
        if isinstance(path, str):
            path = Path(path)
            
        if check and not path.exists():
            raise FileExistsError(f"{path} is not exists")
        return path
    
    def checkfile(self, check_object, path=None, base=None):    # 查找文件
        
        """
            # 查找文件
        check_object: 查找对象
        path: 文件目录
        base: 查找目录
        """
        if base is not None:
            if not isinstance(base, Path):
                base = Path(base)
            if not base.exists():
                raise "check dir is not exists"
        else:
            base = self._disks
        
        if path:
            # 如果不是Path转化为Path
            if not isinstance(path, Path):
                path = Path(path)
            # 如果路径本地本地存在方法它， 校验路径是否存在
            if path.exists():
                return path
        else:
            results: List[Path] = []
            for disk in self._disks:
                for root, dirs, files in os.walk(disk):
                    for file in files:
                        if file == check_object:
                            results.append(os.path.join(root, file))
                    for dir in dirs:
                        if dir == check_object:
                            results.append(os.path.join(root, dir))     
            return results
    
                
    def executor(self, args, *, # shell执行器
                 cwd:Path=None,
                 stdin: str=None,
                 timeout:int=None,
                 iswait:bool=True
                 ):
        """
        :param label: PID标识
        :param args: 封装的shell指令列表
        :return report: 返回报文, 用于向服务端汇报执行结果
        """
        process= subprocess.Popen(
                args=args,
                shell=True, 
                text=True,
                stdin = subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
            )
        if iswait:
            msg, err = process.communicate(input=stdin, timeout=timeout)
        else:
            # time.sleep(0.5)
            if process.poll() is None:
                msg, err = True, False
            else:
                msg, err = False, True
        return msg, err
    
    def format_params(self, typecode:int, data: dict|list) -> str:  # 预定义表单类型
        """
        0: instruct,
        1: software,
        2: report,
        3: download
        """
        types = [
            "instruct",
            "software",
            "report",
            "download"
        ]
        return json.dumps({
            "type": types[typecode],
            "data": data,    # 携带的data， 软件路径列表 | 错误报文
            "cookie": time.time()
        }, ensure_ascii=False)     

            
    def report(self, args, msg, err):# 格式化报文
        return json.dumps({
            "status": "ok" if not err else "error",
            "instruct": " ".join(args) if isinstance(args, Iterable) else args,
            "msg": msg if msg else "<No output>",
            "err": err if err else "<No error output>",
            "time": time.time()
        }, ensure_ascii=False, indent=4)   
    
        
    def init(self):
        pass
    
    # 硬件相关
    def close(self):# 关机
        pass
    
    def restart(self):# 重启
        pass
    
    
    # 软件相关
    def start_software(self, path): # 启动软件
        pass
    
    def close_software(self, softname): # 关闭软件
        pass
    
    # 文件相关
    def compress(self, topath, frompath, mode):
        # 压缩
        pass
    
    def uncompress(self, topath, frompath, suffix):
        topath = self._path(topath, check=True)
        frompath = self._path(frompath, check=True)
        
        if frompath.suffix not in suffix:
            raise Exception(f"source must in {suffix}, actually gives: {frompath}")
        
        packname = frompath.name.split(".")[0] 
        topath = topath.joinpath(packname)
        topath.mkdir(exist_ok=True)
        return topath, frompath
    
    def wget(self, url, path=None):
        # 下载
        pass
    
    def remove(self, path):
        # 移动文件或删除
        pass
            

    def build_hyperlink(self, alias, frompath):
        pass
    
    def uproot(self):
        # 升级root权限
        pass
    
    def record(self, level:int, msg):
        self.logger.record(level, msg)
