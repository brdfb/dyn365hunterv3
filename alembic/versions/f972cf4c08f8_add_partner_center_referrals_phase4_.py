"""add_partner_center_referrals_phase4_fields

Revision ID: f972cf4c08f8
Revises: f786f93501ea
Create Date: 2025-01-30 22:58:59.699068

NOTES:
- Phase 4.1: DB Schema Revision - Add missing columns for Partner Center referrals
- Adds: engagement_id, external_reference_id, substatus, type, qualification, direction,
        customer_name, customer_country, deal_value, currency
- Adds indexes for filtering: direction, substatus
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f972cf4c08f8'
down_revision: Union[str, None] = 'f786f93501ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to partner_center_referrals table
    op.add_column('partner_center_referrals', sa.Column('engagement_id', sa.String(length=255), nullable=True))
    op.add_column('partner_center_referrals', sa.Column('external_reference_id', sa.String(length=255), nullable=True))
    op.add_column('partner_center_referrals', sa.Column('substatus', sa.String(length=50), nullable=True))
    op.add_column('partner_center_referrals', sa.Column('type', sa.String(length=50), nullable=True))
    op.add_column('partner_center_referrals', sa.Column('qualification', sa.String(length=50), nullable=True))
    op.add_column('partner_center_referrals', sa.Column('direction', sa.String(length=50), nullable=True))
    op.add_column('partner_center_referrals', sa.Column('customer_name', sa.String(length=255), nullable=True))
    op.add_column('partner_center_referrals', sa.Column('customer_country', sa.String(length=100), nullable=True))
    op.add_column('partner_center_referrals', sa.Column('deal_value', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('partner_center_referrals', sa.Column('currency', sa.String(length=10), nullable=True))
    
    # Create indexes for filtering (Phase 4.3: Ingestion Filter Rules)
    op.create_index('idx_partner_center_referrals_direction', 'partner_center_referrals', ['direction'], unique=False)
    op.create_index('idx_partner_center_referrals_substatus', 'partner_center_referrals', ['substatus'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_partner_center_referrals_substatus', table_name='partner_center_referrals')
    op.drop_index('idx_partner_center_referrals_direction', table_name='partner_center_referrals')
    
    # Drop columns
    op.drop_column('partner_center_referrals', 'currency')
    op.drop_column('partner_center_referrals', 'deal_value')
    op.drop_column('partner_center_referrals', 'customer_country')
    op.drop_column('partner_center_referrals', 'customer_name')
    op.drop_column('partner_center_referrals', 'direction')
    op.drop_column('partner_center_referrals', 'qualification')
    op.drop_column('partner_center_referrals', 'type')
    op.drop_column('partner_center_referrals', 'substatus')
    op.drop_column('partner_center_referrals', 'external_reference_id')
    op.drop_column('partner_center_referrals', 'engagement_id')
