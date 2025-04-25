from pydantic import BaseModel

class ProductResponse(BaseModel):
    modelid: str
    name: str
    scount: str
    image: str
    price: float
    barcode: str
    codemodel: str
    kmin: int
    volname: str
    wlink: str
    cell: str
    
    class Config:
        orm_mode = True
        extra = "allow"
