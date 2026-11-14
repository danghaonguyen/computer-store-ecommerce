
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Integer,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.products.product import Product


class ProductAttribute(Base):

    __tablename__ = "product_attributes"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "attribute_name",
            name="uq_product_attribute"
        ),
    )

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

    attribute_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    attribute_value: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    product: Mapped["Product"] = relationship(
        back_populates="attributes"
    )