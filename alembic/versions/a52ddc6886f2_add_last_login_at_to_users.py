"""Add last_login_at to users

Revision ID: a52ddc6886f2
Revises: 5709ad826a91
Create Date: 2025-04-09 22:38:01.541508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a52ddc6886f2'
down_revision: Union[str, None] = '5709ad826a91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_login_at')
    # ### end Alembic commands ###
