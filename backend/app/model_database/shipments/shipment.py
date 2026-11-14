from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.orders.order import Order

class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False
    )

    shipping_provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    tracking_number: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True
    )

    shipping_status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        nullable=False
    )

    shipping_fee: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    shipped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    order: Mapped["Order"] = relationship(
        back_populates="shipment"
    )