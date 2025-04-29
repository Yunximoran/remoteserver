# alter 修改一些配置选项
from typing import Annotated

from fastapi import APIRouter, Query
from lib import Resolver
from lib.strtool import pattern
from lib.database import Redis

database = Redis()
resolver = Resolver()
# 接口信息
router = APIRouter()
prefix = "/server/alter"
tags = ["alter"]

@router.put('/alias')
async def setalias(alias, ip:Annotated[str, Query(pattern=pattern.NET_IP)]):
    database.hset("ip_alias", alias, ip)      # 需要暴露
    return {"OK": f"set alias: {alias} -> {ip}"}


@router.put('/reset_classify_name')
async def reset_classify_name(
        oldn: str,
        newn: str
    ):
    if oldn not in database.smembers("classifylist"):
        return {"ERROR": f"{oldn} is not exist"}
    
    # 获取分类数据
    items = database.hget("classify", oldn)
    
    # 删除分类索引
    database.srem("classifylist", oldn)
    database.hdel("classify", oldn)
    
    # 用新类名，重新赋值
    database.sadd("classifylist", newn)
    if items:
        database.hset("classify", newn, items)
    return {"OK": f"set {oldn} -> {newn}"}
    
