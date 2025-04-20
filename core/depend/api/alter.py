# alter 修改一些配置选项
from typing import Annotated

from fastapi import APIRouter, Query
from lib import Resolver
from lib.strtool import pattern
from static import DB

resolver = Resolver()
# 接口信息
router = APIRouter()
prefix = "/server/alter"
tags = ["alter"]


@router.put('/alias')
async def setalias(alias, ip:Annotated[str, Query(pattern=pattern.NET_IP)]):
    DB.hset("ip_alias", alias, ip)      # 需要暴露
    return {"OK": f"set alias: {alias} -> {ip}"}


@router.put('/reset_classify_name')
async def reset_classify_name(
        oldn: str,
        newn: str
    ):
    if oldn not in DB.smembers("classifylist"):
        return {"ERROR": f"{oldn} is not exist"}
    
    # 获取分类数据
    items = DB.hget("classify", oldn)
    
    # 删除分类索引
    DB.srem("classifylist", oldn)
    DB.hdel("classify", oldn)
    
    # 用新类名，重新赋值
    DB.sadd("classifylist", newn)
    if items:
        DB.hset("classify", newn, items)
    return {"OK": f"set {oldn} -> {newn}"}
    
    