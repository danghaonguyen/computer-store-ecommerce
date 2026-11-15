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
    from app.model_database.users.user import User
    from app.model_database.orders.order_item import OrderItem
    from app.model_database.orders.order_status_history import OrderStatusHistory
    from app.model_database.promotions.coupon_usage import CouponUsage
    from app.model_database.reviews.review import Review
    from app.model_database.shipments.shipment import Shipment
    from app.model_database.payments.payment import Payment

class Order(Base):

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        nullable=False
    )

    recipient_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    recipient_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    shipping_province: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    shipping_district: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    shipping_ward: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    shipping_address: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    shipping_fee: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="orders"
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )

    status_history: Mapped[list["OrderStatusHistory"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )

    coupon_usage: Mapped["CouponUsage | None"] = relationship(
        back_populates="order",
        uselist=False
    )

    reviews: Mapped[list["Review"]] = relationship(
        back_populates="order"
    )

    shipment: Mapped["Shipment | None"] = relationship(
        back_populates="order",
        uselist=False
    )

    payment: Mapped["Payment"] = relationship(
        back_populates="order"
    )