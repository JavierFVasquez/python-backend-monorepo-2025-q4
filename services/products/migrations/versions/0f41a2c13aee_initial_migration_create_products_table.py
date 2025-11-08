"""Initial migration - create products table

Revision ID: 0f41a2c13aee
Revises: 
Create Date: 2025-11-07 17:07:46.373299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f41a2c13aee'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'products',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('price', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create indexes
    op.create_index('ix_products_name', 'products', ['name'])
    op.create_index('ix_products_created_at', 'products', ['created_at'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_products_created_at', 'products')
    op.drop_index('ix_products_name', 'products')
    op.drop_table('products')
