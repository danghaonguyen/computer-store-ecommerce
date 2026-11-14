

from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    Integer,
    Numeric
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.products.product import Product
    from app.model_database.carts.cart_item import CartItem
    from app.model_database.carts.wishlist import Wishlist
    from app.model_database.inventory.inventory import Inventory
    from app.model_database.orders.order_item import OrderItem

class ProductVariant(Base):

    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    sku: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    variant_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    compare_at_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    ) 

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    product: Mapped["Product"] = relationship(
        back_populates="variants"
    )

    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="product_variant"
    )

    wishlists: Mapped[list["Wishlist"]] = relationship(
        back_populates="product_variant"
    )

    inventories: Mapped[list["Inventory"]] = relationship(
        back_populates="product_variant"
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product_variant"
    )