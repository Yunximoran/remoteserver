from fastapi import Query
from typing import Annotated
from lib.strtool import pattern
from lib.database import Redis
from pathlib import Path

from ._tables import *

database = Redis()


# ===================HEART PACKAGES===================
def parse_heartpkgs() -> dict:                                                                  # 解析心跳包数据
    return database.loads(database.hgetall(heartpkgs))

def getitem(ip=None, tag=None):                                                                 # 获取指定数据
    heartpkgs = parse_heartpkgs()

    if ip: 
        if ip not in heartpkgs: return None
        return heartpkgs[ip][tag]
    else:  
        if tag is None: return heartpkgs
        return {ip: heartpkgs[ip][tag] for ip in heartpkgs}

def get_netspeed(ip=None):                                                                      # 获取网络带宽
    return getitem("netspeed", ip)

def get_files(ip=None):                                                                         # 获取文件数据
    return getitem(ip, "files")

def get_working(ip=None):                                                                       # 获取工作目录
    return getitem(ip, "working")
 
def get_os(ip=None):                                                                            # 获取系统标识
    return getitem(ip, "os")

def get_mac(ip=None):                                                                           # 获取mac地址
    return getitem(ip, "mac")

def get_softs(ip=None):                                                                         # 获取软件数据
    return getitem(ip, "softwares")


# ===================  CLASSIFY  ===================
def parse_classify():                                                                           # 解析分类表数据
    return database.loads(database.hgetall(classify))


# ================== REPORTS ======================
def parse_reports():                                                                            # 解析汇报数据
    return database.loads(database.hgetall(reports))


# ================ INSTURCTS ====================
def parse_instructs():                                                                          # 解析预存指令
    return database.loads(database.hgetall(instructlist))


# ================ SOFTWARES ====================
def parse_softwares():                                                                          # 解析软件清单
    return database.loads(database.hgetall(softwarelist))


# ================== CHECK DATA ==================
def check_index(ip):                                                                            # 校验连接索引
    return database.hget(clientstatus, ip) is not None

def check_conning(ip):                                                                          # 校验连接状态
    return database.hget(clientstatus, ip) == "true"

def check_classify(cln):                                                                        # 校验分类表索引
    return cln in database.smembers(classifylist)

def check_exits_clients(ip):
    return ip in database.hgetall(clientstatus)

def check_exits_softwares(soft):
    return soft in database.hgetall(softwarelist)

def check_softstatus(ip, soft):                                                                 # 校验软件状态
    softs = get_softs(ip)
    for item in softs:
        if item['ecdis']['name'] == soft:
            return item['conning']
    return False

# =================== DISPOSE ===================
def dispose_soft_information(                                                                   # 处理软件信息
    ip: Annotated[str, Query(pattern=pattern.NET_IP)],
    softname: Annotated[str, "软件名称"]
    ):
    """
        获取不同分类下的软件信息

    :param ip:  软件IP
    :param softname:  软件名称
    :type ip: str query(pattern=pattern.NET_IP)
    :type softname: str

    """
    conning = check_conning(ip)

    # 客户端连接时采取检查软件状态
    if conning: status = check_softstatus(ip, softname)
    else:       status = False
    return status, conning

def dispose_classify_information():                                                             # 处理分类信息
    classify = parse_classify()

    for cln in classify:
        items:list[dict] = classify[cln]
        for item in items:
            soft = item["soft"]
            ip = item["ip"]
            item['status'], item['conning'] = dispose_soft_information(soft, ip)
            item['os'] = get_os(ip)
            item['mac'] = get_mac(ip)
            item['working'] = get_working(ip)
            item['files'] = get_files(ip)
            item['netspeed'] = get_netspeed(ip)
    return classify

def dispose_client_files(filedir:Path):                                                         # 处理文件信息
    files = {file.name: {} for file in filedir.rglob("*") if file.is_file()}
    fileclient = get_files()
    for ip in fileclient:
        ipfiles = fileclient[ip]
        for file in ipfiles:
            if file in files:
                files[file][ip]= {
                    "working": get_working(ip),
                    "schedule": get_files(ip)[file],
                }
    return files
   
def dispose_client_information():                                                               # 处理客户端信息
    # 获取客户端信息
    heart_pkgs = parse_heartpkgs()
    information = {}
    for ip in heart_pkgs:
        information = {
            "os": heart_pkgs[ip]['os'],
            "mac": heart_pkgs[ip]['mac'],
            "working": heart_pkgs[ip]["working"],
            "netspeed": heart_pkgs[ip]['netspeed']
        }
    return information

def dispose_realtime(filepath):                                                                 # 处理实时数据
    """
    实时更新数据
    """
    return {
        "client_reports": parse_reports(),                                      # 客户端控制运行结果汇报
        "instructlist": parse_instructs(),                                      # 预存指令列表
        "softwarelist": parse_softwares(),                                      # 软件列表
        "classify": dispose_classify_information(),                             # 分类数据
        "classifylist": list(database.smembers("classifylist")),                # 分类索引
        "client_information": dispose_client_information(),                     # 客户端信息
        "files": dispose_client_files(filepath)                                 # 文件信息 
    }


if __name__ == "__main__":
    Path.cwd().joinpath("local")
    print(dispose_realtime(Path.cwd().joinpath("local")))