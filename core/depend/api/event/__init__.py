from typing import Annotated, List, AnyStr

from fastapi import APIRouter

from core.depend.control import Control
from datamodel.instruct import Instruct
from datamodel import WaitDesposeResults
from lib.database import Redis


from . import _add_event as add
from . import _pop_event as pop
from . import _set_event as set

database = Redis()
controlor = Control()
router = APIRouter()
prefix="/server/event"
tags = ["event"]

router.include_router(
    router=add.router,
    prefix=add.prefix,
    tags=add.tags
)
router.include_router(
    router=pop.router,
    prefix=pop.prefix,
    tags=pop.tags
)

router.include_router(
    router=set.router,
    prefix=set.prefix,
    tags=set.tags
)

# 激活客户端
@router.put("/wol")
async def magic_client(toclients:List[AnyStr] = []):
    """
        发送唤醒魔术包
    toclients: 指定发送目标IP列表
    """
    try:
        controlor.sendtoclient(toclients, wol=True)
        return {"OK": f"Sent WOL packets to clients"}
    except Exception as e:
        print(f"WOL ERROR: {str(e)}")
        return {"ERROR": f"Failed to send WOL: {str(e)}"}

# 待办事件已处理事件
@router.put("/desposedsoftware")
async def despose_waitdones(res: WaitDesposeResults):
    # 将待办实现处理结果保存redis
    database.hset("waitdone_despose_results", res.cookie, res.results)
    return {"OK": f"disposed: {res.cookie}"}

