
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.users.user import User
    from app.model_database.products.product_variant import ProductVariant


class Wishlist(Base):

    __tablename__ = "wishlists"


    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "product_variant_id",
            name="uq_wishlist_user_product_variant"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    product_variant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="wishlists"
    )

    product_variant: Mapped["ProductVariant"] = relationship(
        back_populates="wishlists"
    )