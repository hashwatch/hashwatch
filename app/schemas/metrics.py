from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Metrics(BaseModel):
    tag:            str
    hashrate:       float
    power:          Optional[float]
    voltage:        Optional[float]
    time:           Optional[datetime] = None

    class Config:
        from_attributes = True