import json
from typing import List, AnyStr
from pathlib import Path
from fastapi import APIRouter, File, UploadFile

from datamodel import SoftwareList
from datamodel.instruct import InstructList, Instruct
from core.depend.protocol.udp import BroadCastor
from core.depend.control import Control

from static import DB
from lib import Resolver

resolver = Resolver()

# 广播发送端配置
BROADCAST= (resolver("sock", "udp", "ip-broad"), resolver("ports", 'udp', "multi")) # 广播发送地址
USENET = (resolver("network", "ip"), resolver("ports", 'udp', "multi")) # 广播使用网卡

broadcastor = BroadCastor(USENET)
controlor = Control()

# 通信接口
router = APIRouter()
prefix = "/server/send"
tags = ["send"]


@router.post("/download")   # 下载文件
async def sendfiles(files:List[AnyStr], toclients: List[AnyStr] = [], instructlist:InstructList = None):
    try:
        files = [Path(file) for file in files]
        instructs = None if instructlist is None else [item.model_dump_json() for item in instructlist.items]
        controlor.sendtoclient(toclients=toclients, files=files, instructs=instructs)
    except Exception as e:
        return {"ERROR": str(e)}
    
@router.post("/instruct")   # 发送控制指令 
async def send_control_shell(instructlist: InstructList, toclients: List[AnyStr] = []):
    """
        发送控制指令
    shell_list: 指令列表 
    toclients: 目标地址
    """
    try:
        
        # 解析请求体
        instructs = [item.model_dump_json() for item in instructlist.items]
        # 发送控制指令
        controlor.sendtoclient(toclients, instructs=instructs) 
        return {"OK": "instructions have been sent to the client"}
    except Exception as e:
        print(e)
        return {"ERROR": str(e)}
    

@router.post("/softwarelist")    # 发送软件清单
async def send_software_checklist(checklist: SoftwareList):
    """
        发送软件清单
    checklist: 软件列表
    """
    
    softwares = json.dumps([item.model_dump() for item in checklist.items], ensure_ascii=False)
    try:
        broadcastor.send(softwares, BROADCAST)  
        return {"OK": f"send software checklist {softwares}"}
    except Exception as e:
        print(e)
        return {"ERROR": str(e)}

@router.post("/start_all_softwares")    # 开启所有软件
async def start_all_softwares(cln:str=None):
    context = DB.hgetall("classify")
    classify = DB.loads(context)
    ip_soft: dict[str, list] = {}
    
    # 遍历所有分类
    if cln is not None:
        # 指定分类
        if cln not in classify:
            return {"ERROR": f"{cln} is not exists"}
        data = classify[cln]
        for item in data:
            soft = item['soft']
            ip = item['ip']
            if ip not in ip_soft:
                ip_soft[ip] = []
                
            HeartPackages =DB.loads(DB.hget("heart_packages", ip))
            ip_soft[ip].append(Instruct(label="start -s", instruct=soft, os=HeartPackages['os']).model_dump_json())
    # 遍历所有分类
    else:
        for cln in classify:
            data = classify[cln]
            for item in data:
                soft = item['soft']
                ip = item['ip']
                # 统计每个ip 对应的软件构造成指令列表
                if ip not in ip_soft:
                    ip_soft[ip] = []
                    
                HeartPackages =DB.loads(DB.hget("heart_packages", ip))
                ip_soft[ip].append(Instruct(label="start -s", instruct=soft, os=HeartPackages['os']).model_dump_json())
                
    for ip in ip_soft:
        controlor.sendtoclient([ip], instructs=ip_soft[ip])

@router.post("/close_all_softwares")    # 关闭所有软件
async def close_all_softwares(cln:str=None):
    context = DB.hgetall("classify")
    classify = DB.loads(context)
    ip_soft: dict[str, list] = {}
    
    if cln is not None:
        if cln not in classify:
            return {"ERROR": f"{cln} is not exists"}
        data = classify[cln]
        for item in data:
            soft = item['soft']
            ip = item['ip']
            if ip not in ip_soft:
                ip_soft[ip] = []
                
            HeartPackages =DB.loads(DB.hget("heart_packages", ip))
            ip_soft[ip].append(Instruct(label="close -s", instruct=soft, os=HeartPackages["os"]).model_dump_json())
    # 遍历所有分类
    else:
        for cln in classify:
            data = classify[cln]
            for item in data:
                soft = item['soft']
                ip = item['ip']
                # 统计每个ip 对应的软件构造成指令列表
                if ip not in ip_soft:
                    ip_soft[ip] = []
                    
                HeartPackages =DB.loads(DB.hget("heart_packages", ip))
                ip_soft[ip].append(Instruct(label="close -s", instruct=soft, os=HeartPackages["os"]).model_dump_json())
    
    for ip in ip_soft:
        controlor.sendtoclient([ip], instructs=ip_soft[ip])
        