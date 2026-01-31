from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ZoneBase(BaseModel):
    borough: str = Field(..., min_length=1)
    zone_name: str = Field(..., min_length=1)
    service_zone: str = "Unknown"
    active: bool = True

class ZoneCreate(ZoneBase):
    id: int = Field(..., gt=0)

class ZoneUpdate(BaseModel):
    borough: Optional[str] = None
    zone_name: Optional[str] = None
    service_zone: Optional[str] = None
    active: Optional[bool] = None

class ZoneResponse(ZoneBase):
    id: int
    created_at: datetime