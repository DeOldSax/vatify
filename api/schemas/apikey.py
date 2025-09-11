from pydantic import BaseModel
from datetime import datetime

class APIKeyCreateIn(BaseModel):
    name: str

class APIKeyListItem(BaseModel):
    id: str
    name: str
    created_at: datetime
    prefix: str
    last4: str
    revoked: bool

class APIKeyCreateOut(APIKeyListItem):
    secret: str  # nur einmal bei Erstellung/Rotation
