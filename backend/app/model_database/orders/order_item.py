from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.orders.order import Order
    from app.model_database.products.product_variant import ProductVariant
    from app.model_database.orders.order_item_inventory import OrderItemInventory

class OrderItem(Base):

    __tablename__ = "order_items"

    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "product_variant_id",
            name="uq_order_item_order_product_variant"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    product_variant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False
    )

    # Product information snapshot at purchase time
    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    variant_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    sku: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    order: Mapped["Order"] = relationship(
        back_populates="items"
    )

    product_variant: Mapped["ProductVariant"] = relationship(
        back_populates="order_items"
    )

    inventory_allocations: Mapped[list["OrderItemInventory"]] = relationship(
        back_populates="order_item",
        cascade="all, delete-orphan"
    )
