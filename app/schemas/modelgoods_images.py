from pydantic import BaseModel
from typing import Optional

class ImageUploadResponse(BaseModel):
    status: str
    filename: str

class ImageInfo(BaseModel):
    modelid: str
    filename: str
    imgext: Optional[str] = None
    changedate: Optional[str] = None

class ImageDeleteResponse(BaseModel):
    status: str
    message: str