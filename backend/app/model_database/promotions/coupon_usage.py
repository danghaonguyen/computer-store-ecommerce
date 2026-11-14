from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.promotions.coupon import Coupon
    from app.model_database.users.user import User
    from app.model_database.orders.order import Order

class CouponUsage(Base):
    __tablename__ = "coupon_usages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    coupon_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("coupons.id", ondelete="RESTRICT"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    coupon: Mapped["Coupon"] = relationship(
        back_populates="usages"
    )

    user: Mapped["User"] = relationship(
        back_populates="coupon_usages"
    )

    order: Mapped["Order"] = relationship(
        back_populates="coupon_usage"
    )