from pydantic import BaseModel
import uuid
from datetime import datetime

class KeysPixCreate(BaseModel):
    type_key: str
    value_key: str

class KeysPixResponse(BaseModel):
    id: uuid.UUID
    type_key: str
    value_key: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}