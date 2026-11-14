from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.products.product_variant import ProductVariant
    from app.model_database.inventory.warehouse import Warehouse
    from app.model_database.inventory.stock_movement import StockMovement


class Inventory(Base):

    __tablename__ = "inventory"

    __table_args__ = (
        UniqueConstraint(
            "warehouse_id",
            "product_variant_id",
            name="uq_warehouse_product_variant"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    warehouse_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False
    )

    product_variant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    reserved_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    warehouse: Mapped["Warehouse"] = relationship(
        back_populates="inventories"
    )

    product_variant: Mapped["ProductVariant"] = relationship(
        back_populates="inventories"
    )

    stock_movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="inventory"
    )