from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

from sqlalchemy import Sequence

if TYPE_CHECKING:
    from app.models.keys_pix import KeysPix
    from app.models.ledger import Ledger
    from app.models.user import User


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "type_account",
                         name="uq_user_type_account"),
        CheckConstraint(
            "type_account IN ('current', 'savings')",
            name="ck_accounts_type_account",
        ),
        CheckConstraint(
            "status IN ('active', 'blocked', 'closed')",
            name="ck_accounts_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    type_account: Mapped[str] = mapped_column(String(20), nullable=False)
    number_account: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    agency: Mapped[str] = mapped_column(
        String(10), nullable=False, default="0001")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="accounts")
    keys_pix: Mapped[list[KeysPix]] = relationship(back_populates="account")
    ledgers: Mapped[list[Ledger]] = relationship(back_populates="account")
