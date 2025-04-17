
import json
import re
from typing import Annotated, List, Set
from fastapi import APIRouter

from lib import Resolver
from datamodel import Classify
from datamodel.transfer_data import SoftwareList
from datamodel.instruct import InstructList
from core.depend.control import Control
from static import DB

resolver = Resolver()
controlor = Control()

# 事件接口
router = APIRouter()
prefix = "/add"
tags = ["add"]

    

# ========= 添加事件 ========== #
@router.put("/softwarelist")    # 添加软件清单
async def addsoftwarelist(softwares: Annotated[SoftwareList, None]):
    """
        添加软件清单
    """
    softs = []
    for info in softwares.items:
        softs.append(info.ecdis.name)
        DB.hset("softwarelist", info.ecdis.name, info.model_dump_json())
    return {"OK": softs}
    
@router.put("/classify")
async def addclissify(classify: Annotated[Classify, None]):
    # classify.items: 不重复列表
    classifylist = DB.smembers("classifylist")
    if classify.name not in classifylist:
        # 如果分类不存在，新建分类
        DB.sadd("classifylist", classify.name)
            
    if classify.items is {}:
        # 如果items没空，只创建分类
        return {"OK": f"created classify: {classify.name}"}

    # 转化为集合，排除重复项
    allconn= DB.hgetall("client_status")
    allsoft = DB.hgetall("softwarelist")
    ignore_conn = []
    ignore_soft = []
    items = []
    if allconn is None:
        return {"ERROR", "没有链接你跟谁绑定"}
    
    for item in classify.items:
        if item.ip not in allconn:
            ignore_conn.append(item.ip)
            continue
        if item.soft not in allsoft and item.soft != "":
            ignore_soft.append(item.soft)
            continue
        items.append(item.model_dump_json())
        
    items = set(items)
    context = DB.hget("classify", classify.name)
    if context:
        clndata = set(json.loads(context))  # 解析json， 并转化为集合
        clndata = list(clndata | items)     # 合并两个集合，转化类列表
    else:
        clndata = list(items)
    
    # 检查IP引用计数
    count = {}   
    for data in clndata:
        item = json.loads(data)
        ip = item['ip']
        if ip in count:
            count[ip] +=1 
        else:
            count[ip] = 0
    
    # 更新引用计数
    for ip in count:
        DB.hset("classified", ip, count[ip])
        
    # 更新数据
    DB.hset("classify", classify.name, json.dumps(clndata, ensure_ascii=False))
    return {"OK": f"update: {clndata}, ignore conn: {ignore_conn}, ignore_soft: {ignore_soft}"}


@router.put("/set_of_prestored_instructions")
async def add_instructions(alias: Annotated[str, None], instructlist: Annotated[InstructList, None]):
    context = instructlist.model_dump_json()
    DB.hset("instructlist", alias, context)
    return {"OK": f"add prestored instruct: {alias} -> {context}"}
