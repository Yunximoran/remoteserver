from typing import Annotated

from fastapi import APIRouter

from datamodel.transfer_data import SoftwareList
from lib.database import Redis
import json

database = Redis()
router = APIRouter()
prefix = "/set"
tags = ["set"]


@router.put("/softwarelist")    # 添加软件清单
async def addsoftwarelist(softwares: Annotated[SoftwareList, None]):
    """
        添加软件清单
    """
    softs = []
    # 删除原来的数据
    database.delete("softwarelist")
    
    # 更新软件清单
    for info in softwares.items:
        softs.append(info.ecdis.name)
        database.hset("softwarelist", info.ecdis.name, info.model_dump_json())
    return {"OK": softs}

# @router.put("/set_filestatus")
# async def set_filestatus(filename, ip, status:list):
#     database.hset(filename, ip, json.dumps(status, ensure_ascii=False, indent=4))
