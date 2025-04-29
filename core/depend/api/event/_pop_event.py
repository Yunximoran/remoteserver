
import re
import json
from typing import Annotated, List, AnyStr
from fastapi import APIRouter, Query

from lib import Resolver
from lib.strtool import pattern
from core.depend.control import Control
from datamodel.classify import ClassIndex
from lib.database import Redis

database = Redis()
resolver = Resolver()
controlor = Control()

# 事件接口
router = APIRouter()
prefix = "/pop"
tags = ["pop event"]


# ========= 移除事件 ========== #
@router.put("/softwarelist")
async def popsoftwarelist(software: Annotated[str, None]):
    """
        # 移除软件清单
    software: 软件名    
    """
    # 获取当前软件清单
    softwarelist = database.lrange("softwarelist")
    
    # 找到对应软件
    for i, item in enumerate(softwarelist):
        if re.match(software, item):
            # 删除修改redis表格
            database.lpop("softwarelist", i)
    return {"OK", f"POP {software}"}


@router.put("/clissify")
async def popclassify(
        cln: Annotated[str, None],
        item: Annotated[ClassIndex, None]
    ):
    # 检查分类是否存在
    classifylist = database.smembers("classifylist")
    if not cln in classifylist:
        return {"ERROR": f"classify: {cln} not exists"}

    # 读取分类数据
    clndata: List[str] = database.loads(database.hget("classify", cln))
    
    context: dict = item.model_dump()
    if context in clndata:
        # 检查引用计数, 将移除引用计数归零的客户端IP
        count:int = database.hget("classified", item.ip)
        database.hdel("classified", item.ip) if int(count) == 0 else database.hset("classified", item.ip, int(count) - 1)
        
        # 更新修改后的数据
        index = clndata.index(context)
        clndata.pop(index)
        database.hset("classify", cln, json.dumps([json.dumps(item) for item in clndata]))
        return {"OK": f"remove {context} from classify: {cln}"}
    return {"ERROR": f"item not in classify: {cln}"}


@router.put("/set_of_prestored_instructions")
async def pop_instructions(alias: Annotated[str, None]):
    database.hdel("instructlist", alias)
    return {"OK": f"remove prestored instruct: {alias}"}
    