from typing import Annotated

from fastapi import Query
from pydantic import BaseModel


# 用户模型
class Credentils(BaseModel):
    """
        登录凭证
    校验账户和密码
    """
    account: Annotated[str, None]
    password: Annotated[str, None]
    
    
    
class User(BaseModel):
    account: Annotated[str, None]
    username: Annotated[str, None]
    
class UserResponse(User):
    pass

class NewUser(User):
    password: Annotated[str, None]
    repassword: Annotated[str, None]
    