# ===== 通信模型 ===== #

from typing import Annotated, List

from fastapi import Query
from pydantic import BaseModel
from pathlib import Path
from lib.strtool import pattern

# 软件模型
class Ecdis(BaseModel):
    """
        软件状态
    """
    name: Annotated[str, None]
    executable: Annotated[str, None]
    path:Annotated[str, None]
    

class Software(BaseModel):
    """
        软件模型
    ecdis：心电图， 软件参数
    conning：软件状态
    """
    ecdis: Annotated[Ecdis, None]
    conning: Annotated[bool, None] = False
    
class SoftwareList(BaseModel):
    """
        软件清单
    """
    items: list[Software]
    

class SendSoftWares(SoftwareList):
    multicast: Annotated[str, Query(pattern.NET_IP)]

