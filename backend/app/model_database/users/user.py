
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Boolean, 
    DateTime,
    Integer,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.model_database.users.user_role import user_roles

if TYPE_CHECKING:
    from app.model_database.users.role import Role
    from app.model_database.users.address import Address
    from app.model_database.carts.cart import Cart
    from app.model_database.carts.wishlist import Wishlist
    from app.model_database.orders.order import Order
    from app.model_database.orders.order_status_history import OrderStatusHistory
    from app.model_database.promotions.coupon_usage import CouponUsage
    from app.model_database.reviews.review import Review
    from app.model_database.notifications.notification import Notification



class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
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

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
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

    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users"
    )

    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    cart: Mapped["Cart | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    wishlists: Mapped[list["Wishlist"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user"
    )

    changed_order_statuses: Mapped[list["OrderStatusHistory"]] = relationship(
        back_populates="changed_by_user"
    )

    coupon_usages: Mapped[list["CouponUsage"]] = relationship(
        back_populates="user"
    )

    reviews: Mapped[list["Review"]] = relationship(
        back_populates="user"
    )

    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
