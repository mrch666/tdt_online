from pydantic import BaseModel

class ModelgoodsCreate(BaseModel):
    typeid: str
    firmaid: str
    name: str
    userid: str

class ModelgoodsResponse(ModelgoodsCreate):
    id: str
    class Config:
        orm_mode = True
