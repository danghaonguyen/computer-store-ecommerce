from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.inventory.stock_movement import StockMovement

class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False
    )

    contact_person: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    stock_movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="supplier"
    )