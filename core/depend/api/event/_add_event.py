
import json
import re
from typing import Annotated, List, Set
from fastapi import APIRouter

from lib import Resolver
from datamodel import Classify
from datamodel.transfer_data import SoftwareList
from datamodel.instruct import InstructList
from core.depend.control import Control
from lib.database import Redis

from .._method.get import (
    check_classify,
    check_exits_softwares,
    check_exits_clients,
    check_conning
)
from .._method.get import (
    parse_softwares
)

database = Redis()

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
        database.hset("softwarelist", info.ecdis.name, info.model_dump_json())
    return {"OK": softs}
    
@router.put("/classify")
async def addclissify(classify: Annotated[Classify, None]):
    allconn = database.hgetall("client_status")
    if allconn is None:
        return {"ERROR", "没有链接你跟谁绑定"}
    
    # classify.items: 不重复列表
    if  not check_classify(classify.name):
        # 如果分类不存在，新建分类
        database.sadd("classifylist", classify.name)
            
    if classify.items is {}:
        # 如果items没空，只创建分类
        return {"OK": f"created classify: {classify.name}"}

    # 转化为集合，排除重复项
    allsoft = database.hgetall("softwarelist")
    ignore_conn = []
    ignore_soft = []
    items = []
    for item in classify.items:
        if not check_exits_clients(item.ip):
            # 忽略未连接的IP
            ignore_conn.append(item.ip)
            continue
        if not check_exits_softwares(item.soft) and item.soft != "":
            # 忽略未添加的软件
            ignore_soft.append(item.soft)
            continue
        items.append(item.model_dump_json())
        
    items = set(items)
    context = database.hget("classify", classify.name)
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
        database.hset("classified", ip, count[ip])
        
    # 更新数据
    database.hset("classify", classify.name, json.dumps(clndata, ensure_ascii=False))
    return {"OK": f"update: {clndata}, ignore conn: {ignore_conn}, ignore_soft: {ignore_soft}"}


@router.put("/set_of_prestored_instructions")
async def add_instructions(alias: Annotated[str, None], instructlist: Annotated[InstructList, None]):
    context = instructlist.model_dump_json()
    database.hset("instructlist", alias, context)
    return {"OK": f"add prestored instruct: {alias} -> {context}"}
