import os
import json
import sys
import ctypes
import string
import re
import zipfile, tarfile

from pathlib import Path
from ._base import __BaseSystem



def _uproot():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
        
class Windows(__BaseSystem):
    def __init__(self, *args):
        super().__init__(*args)
        self._disks = self.__getdisks()
    
    def __getdisks(self):
        # window独有
        drives = []
        bitmask = ctypes.cdll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(Path(f"{letter}:\\"))
            bitmask >>= 1
        return drives
    
    def compress(self, topath, frompath, mode=None):
        topath = self._path(topath, check=True) # 压缩到
        frompath = self._path(frompath, check=True) # 压缩目标
        
        if not frompath.is_dir():
            raise Exception(f"{frompath} must a dir")
        
        # 创建压缩文件
        topath = topath.joinpath(".".join((frompath.stem, "zip")))
        with zipfile.ZipFile(topath, "w") as zip:\
        [zip.write(item, arcname=item.relative_to(frompath))\
            for item in frompath.rglob("*")]
                
    
    def uncompress(self, topath, frompath, clear=False):
        # 
        topath, frompath = super().uncompress(topath, frompath, (r".zip",))
        with zipfile.ZipFile(frompath, "r") as zip:
            zip.extractall(topath)
            
        if clear:
            frompath.unlink()
            
    def close(self):
        # 关机
        os.system("shutdown /s /t 3")
        return self.report(['shutdown', "/s", "/t", 1], "closed", False)
    
    def restart(self):
        # 重启
        os.system("shutdown /r /t 3")
        return self.report(["shutdown", "/r", "/t", 1], "restarted", False)
    
    def start_software(self, path):
        # 读取本地软件清单
        path = self._path(path)
        report = self.executor(["start", path.name], cwd=path.parent, iswait=False)
        return report

            
    def close_software(self, path):
        """
            目标软件的唯一路径[实际地址]
        遍历进程池
        
        """
        # 执行关闭软件命令
        path = self._path(path)
        processes = self._check_soft_status(path)
        for process in processes:
            process.kill()
        
        return self.report(path.stem, f"{path} is killed", False)

    
    def build_hyperlink(self, topath:Path, frompath:Path):
        """
            建立软连接
        :param filename: 指定软件名称
        :param frompath: 本地软件地址
        """
        topath = self._path(topath)
        frompath = self._path(frompath)
        if not frompath.exists():
            raise "source file is not exists"
    
        if topath.exists():
            topath.unlink()
            
        # 创建软件映射地址
        topath = str(topath)
        frompath = str(frompath)
        
        # mlink 映射地址 实际地址
        report = self.executor(["mklink", topath, frompath], isadmin=True)
        return topath, report

    def executor(self, args, isadmin=False, *, cwd=None, iswait=True):
        """
            shell执行器
        args: 执行的shell指令
        """
         # 是否需要管理员运行,需要检查当前权限状态，如无管理员权限则进行提权
        _uproot()  if isadmin else None
        
        # 执行shell， 获取其输出信息和异常信息
        msg, err =  super().executor(args, cwd=cwd, iswait=iswait)
        # 返回执行结果， 检查是否由于权限导致的错误，如果是，改用管理员运行
        self.record(1, f"exec {args} results:\n{msg}")
        return self.report(args, msg, err)\
        if not re.match("权限", str(err))\
        else self.executor(args, isadmin=True, cwd=cwd, iswait=iswait)
