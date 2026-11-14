from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Integer,
    Text,
    Boolean,
    DateTime,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.inventory.inventory import Inventory


class Warehouse(Base):

    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    address: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
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

    inventories: Mapped[list["Inventory"]] = relationship(
        back_populates="warehouse"
    )
    