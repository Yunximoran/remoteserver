import json
import asyncio
from typing import Annotated, AnyStr
from pathlib import Path
from fastapi import(
    APIRouter,
    Query
)

from lib import Resolver
from lib.database import Redis
from lib.sys.system import Information

from ._method.get import dispose_realtime


OS = Information.OS
resolver = Resolver()
database = Redis()
filepath = resolver("path", "local")


# 数据接口
router = APIRouter()
prefix = "/server/data"
tags = ["data"]

@router.get("/realtime")
async def realtime():
    # 实时数据
    return dispose_realtime(filepath.path)

@router.get("/softwarelsit")
async def get_softwarelist():
    return {"softwarelist": database.loads(database.hgetall("softwarelist"))}   # 软件列表


@router.get("/iter_local_instructs")    # 遍历脚本目录
async def get_instructs():
    if OS == "Windows":
        suffix = r"*.bat"
    elif OS == "Linux":
        suffix = r"*.sh"
    instructs = resolver("path", "local", "instructs")
    pracpath = instructs.bind(Path.cwd())
    allinstructs = []
    if pracpath.exists() and pracpath.is_dir():
        allinstructs.extend(pracpath.glob(r"*.bat"))
        allinstructs.extend(pracpath.glob(r"*.sh"))
        return allinstructs

@router.get("/iter_local_packages") # 遍历压缩包目录
async def get_packages():
    packages = resolver("path", "local", "packs")
    pracpath = packages.bind(Path.cwd())
    allpacks = []
    if pracpath.exists() and pracpath.is_dir():
        allpacks.extend(pracpath.glob(r"*.zip")) 
        allpacks.extend(pracpath.glob(r"*.tar")) 
        allpacks.extend(pracpath.glob(r"*.gz")) 
        allpacks.extend(pracpath.glob(r"*.bz")) 
        return allpacks

@router.get("/not_classified")
async def get_not_classified():
    classified = set(database.hgetall("classified"))
    allclients = set(database.hgetall("client_status"))   # 获取全部连接客户端
    noclassified = allclients - classified
    return {
        "classified": classified,
        "notclassified": noclassified
    }
    
@router.get("/check_dirs")
async def iter_dir(base:str=None):
    path = Path(base)
    if path.exists() and path.is_dir() and base is not None:
        return {path.glob("*")}
    else:
        return {"ERROR": f"{base} is not exists or not a dir"}