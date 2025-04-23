import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from core.depend.api import (
    alter,
    data,
    event,
    send
)

APP = FastAPI()



ORIGINS = [
    # 前端地址
    "https://localhost:8080",
    "http://localhost:8080",
]

APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# 导入路由
APP.include_router(
    alter.router,
    prefix=alter.prefix,
    tags=alter.tags
)

APP.include_router(
    data.router,
    prefix=data.prefix,
    tags=data.tags
)

APP.include_router(
    event.router,
    prefix=event.prefix,
    tags=event.tags
)

APP.include_router(
    send.router,
    prefix=send.prefix,
    tags=send.tags
)


SERVER = uvicorn.Server(uvicorn.Config(APP))