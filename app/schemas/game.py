from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

class GameImages(BaseModel):
    thumbnail: Optional[HttpUrl] = None
    header: Optional[HttpUrl] = None

class SystemRequirements(BaseModel):
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    ram: Optional[str] = None

class GameBase(BaseModel):
    title: str
    description: str
    genres: List[str]
    platforms: List[str]
    developer: str
    images: Optional[GameImages] = None
    system_requirements: Optional[SystemRequirements] = None
    active: bool = True

class GameCreate(GameBase):
    pass

class GameUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    genres: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    developer: Optional[str] = None
    images: Optional[GameImages] = None
    system_requirements: Optional[SystemRequirements] = None
    active: Optional[bool] = None

class GameResponse(GameBase):
    id: int
    slug: str

    class Config:
        from_attributes = True

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
