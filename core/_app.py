import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from lib.init import Resolver
from .depend.api import (
    alter,
    data,
    event,
    send
)



resolver = Resolver()
cors = resolver("server", 'cors')
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors.data,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# 导入路由
app.include_router(
    alter.router,
    prefix=alter.prefix,
    tags=alter.tags
)

app.include_router(
    data.router,
    prefix=data.prefix,
    tags=data.tags
)

app.include_router(
    event.router,
    prefix=event.prefix,
    tags=event.tags
)

app.include_router(
    send.router,
    prefix=send.prefix,
    tags=send.tags
)
SERVER = uvicorn.Server(uvicorn.Config(app))
