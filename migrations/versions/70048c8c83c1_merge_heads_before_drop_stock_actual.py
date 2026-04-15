"""merge heads before drop stock_actual

Revision ID: 70048c8c83c1
Revises: 7f3c2d9a1b4e, f6b0c0d4a123
Create Date: 2026-04-15 13:07:27.285482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70048c8c83c1'
down_revision = ('7f3c2d9a1b4e', 'f6b0c0d4a123')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
