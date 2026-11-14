from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.payments.payment import Payment

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    payment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=False
    )

    transaction_code: Mapped[str | None] = mapped_column(
        String(150),
        unique=True,
        nullable=True
    )

    transaction_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    transaction_status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    gateway_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    payment: Mapped["Payment"] = relationship(
        back_populates="transactions"
    )