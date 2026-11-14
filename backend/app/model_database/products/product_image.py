
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Boolean,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.products.product import Product


class ProductImage(Base):

    __tablename__ = "product_images"

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

    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    alt_text: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    product: Mapped["Product"] = relationship(
        back_populates="images"
    )