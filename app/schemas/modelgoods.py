from pydantic import BaseModel
from typing import Optional


class ModelgoodsResponse(BaseModel):
    id: str
    name: str
    typeid: str
    firmaid: str
    userid: str

    class Config:
        orm_mode = True

class ModelgoodsCreate(BaseModel):
    id: str
    name: str
    typeid: str
    firmaid: str
    userid: str

    class Config:
        orm_mode = True

class StorageSearchResponse(BaseModel):
    id: str
    name: str
    typeid: str
    firmaid: str
    userid: str
    count: str
    image: str
    price: int
    barcode: Optional[str]
    codemodel: Optional[str]
    volname: Optional[str]
    wlink: Optional[str]
    cell: Optional[str]

    class Config:
        orm_mode = True
