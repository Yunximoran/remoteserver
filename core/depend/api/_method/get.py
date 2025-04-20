from fastapi import Query
from typing import Annotated
from lib.strtool import pattern
from static import DB
from pathlib import Path

def parse_heartpkgs() -> dict:   # 解析心跳包数据
    heart_packages = DB.loads(DB.hgetall("heart_packages"))
    return heart_packages

def get_netspeed(ip=None):  # 获取网络带宽
    heartpkgs = parse_heartpkgs()
    if ip:
        return heartpkgs[ip]['netspeed']
    else:
        return {ip: heartpkgs[ip]['netspeed'] for ip in heartpkgs}

def get_files(ip=None):
    heartpkgs = parse_heartpkgs()
    if ip:
        return heartpkgs[ip]['files']
    else:
        return {ip:heartpkgs[ip]['files'] for ip in heartpkgs}

def get_working(ip=None):   # 获取工作目录
    heartpkgs = parse_heartpkgs()
    if ip:
        return heartpkgs[ip]['working']
    else:
        return {ip: heartpkgs[ip]['working'] for ip in heartpkgs}
 

def get_os(ip=None):
    heartpkgs= parse_heartpkgs()
    if ip:
        return heartpkgs[ip]['os']
    else:
        return {ip: heartpkgs[ip]['os'] for ip in heartpkgs}
    
def get_soft_information(   # 获取软件信息
    cln: Annotated[str, "分类名称"], 
    softname: Annotated[str, "软件名称"],
    ip: Annotated[str, Query(pattern=pattern.NET_IP)]
    ):
    """
        获取不同分类下的软件信息
    """
    mac = None
    status = False
    conning = False
    classifylist = DB.smembers("classifylist")
    if cln not in classifylist:
        return None, None, None # {"ERROR": f"classify: {cln} is not exists"}
    
    info = DB.loads(DB.hget("heart_packages", ip))
    if info is None:
        return None, None, None # {"ERROR": f"client: {ip} never conected"}
    else:
        mac = info['mac']
        conning = DB.hget("client_status", ip) == "true"
        
        # 客户端连接时，软件才去检查软件是否启动
        if conning:
            softwares = info['softwares']
            for soft in softwares:
                if softname == soft['ecdis']['name'] and soft['conning']:
                    status = True
                else:
                    continue
                
    return mac, status, conning

def get_classify(): # 获取分类数据
    classify = DB.loads(DB.hgetall("classify"))

    for cln in classify:
        items:list[dict] = classify[cln]

        for item in items:

            soft = item["soft"]
            ip = item["ip"]
            item['mac'], item['status'], item['conning'] = get_soft_information(cln, soft, ip)
            item['os'] = get_os(ip)
            item['working'] = get_working(ip)
            item['files'] = get_files(ip)
    return classify

def get_client_files(filedir:Path):
    files = {file.name: {} for file in filedir.rglob("*") if file.is_file()}
    fileclient = get_files() # {ip: {file: 11%}}
    for ip in fileclient:
        ipfiles = fileclient[ip]
        for file in ipfiles:
            if file in files:
                files[file][ip]=ipfiles[file]
    return files




   
def get_client_information():   # 获取客户端信息
    heart_pkgs = parse_heartpkgs()
    information = {}
    for ip in heart_pkgs:
        information = {
            "os": heart_pkgs[ip]['os'],
            "working": heart_pkgs[ip]["working"],
            "netspeed": heart_pkgs[ip]['netspeed']
        }
    return information
if __name__ == "__main__":
    print(get_classify())