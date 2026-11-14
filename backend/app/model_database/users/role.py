
from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.database.base import Base
from app.model_database.users.user_role import user_roles

if TYPE_CHECKING:
    from app.model_database.users.user import User

class Role(Base):

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    users: Mapped[list["User"]] = relationship(
        secondary=user_roles, 
        back_populates="roles"
    )