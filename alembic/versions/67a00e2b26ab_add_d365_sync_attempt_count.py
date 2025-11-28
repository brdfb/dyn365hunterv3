"""add_d365_sync_attempt_count

Revision ID: 67a00e2b26ab
Revises: 1b980e76fe86
Create Date: 2025-01-30 14:30:00.000000

NOTES:
- Adds d365_sync_attempt_count field to companies table (P0-3: Sync Attempt Count)
- Tracks number of D365 push attempts for debugging and retry logic
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '67a00e2b26ab'
down_revision: Union[str, None] = '1b980e76fe86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add d365_sync_attempt_count field to companies table
    # P0-3: Sync Attempt Count - tracks number of D365 push attempts
    op.add_column(
        'companies',
        sa.Column('d365_sync_attempt_count', sa.Integer(), nullable=True, server_default='0')
    )
    op.create_index(
        'idx_companies_d365_sync_attempt_count',
        'companies',
        ['d365_sync_attempt_count']
    )


def downgrade() -> None:
    # Drop index and column
    op.drop_index('idx_companies_d365_sync_attempt_count', table_name='companies')
    op.drop_column('companies', 'd365_sync_attempt_count')
