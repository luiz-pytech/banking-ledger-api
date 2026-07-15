from pydantic import BaseModel
from datetime import datetime
import uuid

class AccountCreate(BaseModel):
    type_account: str

class AccountResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type_account: str
    number_account: str
    agency: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}