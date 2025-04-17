from typing import Annotated, List, Dict

from fastapi import Query
from pydantic import BaseModel

from lib.strtool import pattern

class Instruct(BaseModel):
    label: Annotated[str, None]
    instruct: Annotated[str, None]
    isadmin: Annotated[bool, None] = False
    os: Annotated[str, Query(pattern=pattern.TAG_OS, default="Windows")]
    kwargs: Annotated[Dict, None] = {}
    
class InstructList(BaseModel):
    items: List[Instruct]
    # N = Annotated[str, None]
    
    
TYPE = {
    "linux": [],
    "windows": []
}


if __name__ == "__main__":
    InstructList.items