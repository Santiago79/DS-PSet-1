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

class RouteBase(BaseModel):
    pickup_zone_id: int = Field(..., gt=0)
    dropoff_zone_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=3)
    active: bool = True

class RouteCreate(RouteBase):
    pass

class RouteUpdate(BaseModel):
    pickup_zone_id: Optional[int] = Field(None, gt=0)
    dropoff_zone_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=3)
    active: Optional[bool] = None

class RouteResponse(RouteBase):
    id: int
    created_at: datetime