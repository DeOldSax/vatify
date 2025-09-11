from pydantic import BaseModel
from typing import Dict

class UsageOut(BaseModel):
    total: int
    by_endpoint: Dict[str, int]
