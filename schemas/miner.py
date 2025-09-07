from pydantic import BaseModel
from typing import Optional


class Miner(BaseModel):
    tag:        str
    name:       Optional[str]
    model:      Optional[str]
    is_active:  Optional[bool] = False


