from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AdvertisementBase(BaseModel):
    title: str
    description: str
    price: int
    author: str

class AdvertisementCreate(AdvertisementBase):
    pass

class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    author: Optional[str] = None

class AdvertisementResponse(AdvertisementBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True