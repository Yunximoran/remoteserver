from typing import Annotated

from fastapi import APIRouter

from datamodel.transfer_data import SoftwareList
from static import DB


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
    DB.delete("softwarelist")
    
    # 更新软件清单
    for info in softwares.items:
        softs.append(info.ecdis.name)
        DB.hset("softwarelist", info.ecdis.name, info.model_dump_json())
    return {"OK": softs}