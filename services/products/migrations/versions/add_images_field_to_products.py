"""add images field to products

Revision ID: b1c2d3e4f5a6
Revises: 0f41a2c13aee
Create Date: 2025-11-08 12:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: str | Sequence[str] | None = '0f41a2c13aee'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - add images field."""
    op.add_column(
        'products',
        sa.Column('images', JSON, nullable=False, server_default='[]')
    )


def downgrade() -> None:
    """Downgrade schema - remove images field."""
    op.drop_column('products', 'images')

