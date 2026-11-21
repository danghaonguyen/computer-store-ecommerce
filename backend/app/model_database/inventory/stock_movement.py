from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:   
    from app.model_database.inventory.inventory import Inventory
    from app.model_database.inventory.supplier import Supplier

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    inventory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("inventory.id", ondelete="RESTRICT"),
        nullable=False
    )

    supplier_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=True
    )

    movement_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
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

    inventory: Mapped["Inventory"] = relationship(
        back_populates="stock_movements"
    )

    supplier: Mapped["Supplier | None"] = relationship(
        back_populates="stock_movements"
    )