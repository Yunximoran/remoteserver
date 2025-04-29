from typing import Annotated
from pydantic import BaseModel


from .user import User, UserResponse, NewUser, Credentils
from .transfer_data import *
from .instruct import *
from .classify import Classify


class ShellList(BaseModel):
    name: Annotated[str, None]
    shell: Annotated[str, None]
    isadmin: Annotated[bool, None] = False
    os: Annotated[str, None] = Query(pattern="^(Windows)$|^(Linux)$|^(MacOS)$", default="Windows")
    

class WaitDesposeResults(BaseModel):
    cookie: Annotated[float, None]
    results: Annotated[str, None]