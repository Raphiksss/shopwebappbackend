"""Add cascade to FK categories_title

Revision ID: 60087dcca34e
Revises: 63188f0bb23d
Create Date: 2026-02-18 08:13:02.912777

"""

from alembic import op
from typing import Sequence, Union

revision: str = '60087dcca34e'
down_revision: Union[str, None] = '63188f0bb23d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
    'products_category_title_fkey',
    'products',
    type_ = 'foreignkey'
    )
    op.create_foreign_key(
        'products_category_title_fkey',
        'products',
        'categorys',
        ['category_title'],
        ['title'],
        onupdate='CASCADE'
    )

# Создаём новое с ON UPDATE CASCADE




def downgrade() -> None:
   # Возвращаем как было (без CASCADE)
    op.drop_constraint(
    'products_category_title_fkey',
    'products',
    type_ = 'foreignkey'
)
    op.create_foreign_key(
    'products_category_title_fkey',
    'products',
    'categorys',
    ['category_title'],
    ['title']
)