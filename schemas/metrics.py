from pydantic import BaseModel
from typing import Optional


class MinerData(BaseModel):
    tag:            str
    hashrate:       float
    power:          Optional[float]
    voltage:        Optional[float]