from typing import Annotated, AnyStr, Final
from pydantic import BaseModel

class Waitdone(BaseModel):
    pass

class DisposeResults(BaseModel):
    cookie: Annotated[float, None]
    results: Annotated[str, None]