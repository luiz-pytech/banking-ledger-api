from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class TransactionRead(BaseModel):
    id: uuid.UUID
    type: str
    status: str
    value: Decimal
    account_origin_id: uuid.UUID | None
    account_destination_id: uuid.UUID | None
    created_at: datetime
    concluded_at: datetime | None

    model_config = {"from_attributes": True}


class TransferRequest(BaseModel):

    account_origin_id: uuid.UUID
    account_destination_id: uuid.UUID
    value: Decimal = Field(gt=0)
    idempotency_key: str = Field(min_length=8, max_length=255)

    @field_validator("value")
    @classmethod
    def value_must_have_two_decimals(cls, v: Decimal) -> Decimal:
        exp = v.as_tuple().exponent
        try:
            exp_int = int(exp)
        except (TypeError, ValueError):
            return v
        if exp_int < -2:
            raise ValueError("value não pode ter mais de 2 casas decimais")
        return v
 
    @field_validator("account_destination_id")
    @classmethod
    def origin_and_destination_must_differ(cls, v, info):
        origin = info.data.get("account_origin_id")
        if origin is not None and v == origin:
            raise ValueError("account_origin_id e account_destination_id não podem ser iguais")
        return v
