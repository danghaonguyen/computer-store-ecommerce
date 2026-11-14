
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.products.category import Category
    from app.model_database.products.brand import Brand
    from app.model_database.products.product_variant import ProductVariant
    from app.model_database.products.product_attribute import ProductAttribute
    from app.model_database.products.product_image import ProductImage
    from app.model_database.reviews.review import Review

class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False
    )

    brand_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("brands.id", ondelete="RESTRICT"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text, 
        nullable=True
    )

    base_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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

    category: Mapped["Category"] = relationship(
        back_populates="products"
    )

    brand: Mapped["Brand"] = relationship(
        back_populates="products"
    )

    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )

    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )

    attributes: Mapped[list["ProductAttribute"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )

    reviews: Mapped[list["Review"]] = relationship(
        back_populates="product"
    )