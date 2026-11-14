from sqlalchemy import Table, Column, ForeignKey, Integer

from app.database.base import Base


user_roles = Table(
    "user_roles",
    Base.metadata, 

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    ),

    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True
    )
)