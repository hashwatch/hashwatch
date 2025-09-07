from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Metrics(BaseModel):
    tag:            str
    hashrate:       float
    power:          Optional[float]
    voltage:        Optional[float]
    time:           datetime

    class Config:
        orm_mode = True