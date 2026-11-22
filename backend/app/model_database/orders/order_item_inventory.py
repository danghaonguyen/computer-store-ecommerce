
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.orders.order_item import OrderItem
    from app.model_database.inventory.inventory import Inventory


class OrderItemInventory(Base):

    __tablename__ = "order_item_inventories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    order_item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("order_items.id", ondelete="CASCADE"),
        nullable=False
    )

    inventory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("inventory.id", ondelete="RESTRICT"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    order_item: Mapped["OrderItem"] = relationship(
        back_populates="inventory_allocations"
    )

    inventory: Mapped["Inventory"] = relationship(
        back_populates="order_item_allocations"
    )
