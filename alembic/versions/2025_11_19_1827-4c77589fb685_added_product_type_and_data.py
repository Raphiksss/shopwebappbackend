"""Added Product-type and data

Revision ID: 4c77589fb685
Revises: ee920da6fdf9
Create Date: 2025-11-19 18:27:23.052518

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "4c77589fb685"
down_revision: Union[str, None] = "ee920da6fdf9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # autogenerate never emits CREATE TYPE for a new enum, so the type is created here.
    # create_type=False keeps add_column from emitting it a second time.
    processing_mode = postgresql.ENUM(
        "instantly", "notinstantly", name="processing_mode", create_type=False
    )
    processing_mode.create(op.get_bind(), checkfirst=True)

    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "product_type",
                processing_mode,
                server_default="notinstantly",
                nullable=False,
            )
        )
        batch_op.add_column(sa.Column("product_data", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.drop_column("product_data")
        batch_op.drop_column("product_type")

    postgresql.ENUM(name="processing_mode").drop(op.get_bind(), checkfirst=True)
