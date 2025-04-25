from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    peopleid: str
    rangid: str

class UserResponse(UserCreate):
    id: str
    class Config:
        orm_mode = True
