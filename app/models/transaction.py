from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.ledger import Ledger


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "account_origin_id IS NOT NULL OR account_destination_id IS NOT NULL",
            name="ck_transaction_has_origin_or_destination",
        ),
        CheckConstraint(
            "type IN ('transfer_pix', 'deposit', 'withdrawal', 'reversal')",
            name="ck_transactions_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'finished', 'failed', 'reversed')",
            name="ck_transactions_status",
        ),

        CheckConstraint("value > 0", name="ck_transactions_value_positive"),
        CheckConstraint("account_origin_id IS DISTINCT FROM account_destination_id", name="ck_transaction_origin_destination_different")
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    account_origin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )
    account_destination_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    concluded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    origin_account: Mapped[Account | None] = relationship(
        foreign_keys=[account_origin_id]
    )
    destination_account: Mapped[Account | None] = relationship(
        foreign_keys=[account_destination_id]
    )
    ledgers: Mapped[list[Ledger]] = relationship(back_populates="transaction")
