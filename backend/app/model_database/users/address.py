
from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    Integer
)
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.model_database.users.user import User

class Address(Base):

    __tablename__ = "addresses"

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

    recipient_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    province: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    district: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    ward: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    street_address: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="addresses"
    )