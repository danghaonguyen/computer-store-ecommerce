"""update supplier management

Revision ID: 4115428ce77f
Revises: 8c1b3c015f64
Create Date: 2026-11-21 17:45:55.001363

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4115428ce77f"
down_revision: Union[str, Sequence[str], None] = "8c1b3c015f64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        op.f("stock_movements_supplier_id_fkey"), "stock_movements", type_="foreignkey"
    )

    op.create_foreign_key(
        "fk_stock_movements_supplier_id_suppliers",
        "stock_movements",
        "suppliers",
        ["supplier_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.add_column(
        "suppliers",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_unique_constraint("uq_suppliers_name", "suppliers", ["name"])


def downgrade() -> None:
    op.drop_constraint("uq_suppliers_name", "suppliers", type_="unique")

    op.drop_column("suppliers", "is_active")

    op.drop_constraint(
        "fk_stock_movements_supplier_id_suppliers",
        "stock_movements",
        type_="foreignkey",
    )

    op.create_foreign_key(
        op.f("stock_movements_supplier_id_fkey"),
        "stock_movements",
        "suppliers",
        ["supplier_id"],
        ["id"],
        ondelete="SET NULL",
    )
