"""Fix

Revision ID: fed2a10f83da
Revises: bced35cafb66
Create Date: 2025-11-02 13:18:03.943791

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "fed2a10f83da"
down_revision: Union[str, None] = "bced35cafb66"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # No-op: products.category_title is never created by an earlier revision. It existed
    # only in the developer database built by create_all, which is what autogenerate
    # diffed against when this revision was written. The next revision adds the column.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
