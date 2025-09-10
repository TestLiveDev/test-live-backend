"""Create Schema

Revision ID: 20e74310343a
Revises: d2dbbf5f76d1
Create Date: 2025-09-09 16:54:07.682725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20e74310343a'
down_revision: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('create schema testlive')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('drop schema testlive')
