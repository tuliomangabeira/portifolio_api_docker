"""Add relationship itens

Revision ID: 8c217020fabb
Revises: 1cdc2d516a49
Create Date: 2025-07-03 08:58:33.637118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c217020fabb'
down_revision: Union[str, Sequence[str], None] = '1cdc2d516a49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pedidos', 'item')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pedidos', sa.Column('item', sa.VARCHAR(), nullable=True))
    # ### end Alembic commands ###
