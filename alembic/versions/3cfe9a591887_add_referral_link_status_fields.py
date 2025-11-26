"""add_referral_link_status_fields

Revision ID: 3cfe9a591887
Revises: f972cf4c08f8
Create Date: 2025-11-27 02:07:37.605987

NOTES:
- Phase 1: Referrals as First-Class Citizens
- Adds: link_status, raw_domain, linked_lead_id (without FK constraint for v1)
- Enables tracking of unlinked referrals (domain_not_found cases)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cfe9a591887'
down_revision: Union[str, None] = 'f972cf4c08f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add link_status column ('auto_linked' | 'multi_candidate' | 'unlinked')
    op.add_column('partner_center_referrals', 
        sa.Column('link_status', sa.String(length=50), nullable=True))
    
    # Add raw_domain column (original domain before normalization)
    op.add_column('partner_center_referrals', 
        sa.Column('raw_domain', sa.String(length=255), nullable=True))
    
    # Add linked_lead_id column (Integer, no FK constraint for v1)
    op.add_column('partner_center_referrals', 
        sa.Column('linked_lead_id', sa.Integer(), nullable=True))
    
    # Create indexes for filtering
    op.create_index('idx_partner_center_referrals_link_status', 
        'partner_center_referrals', ['link_status'], unique=False)
    op.create_index('idx_partner_center_referrals_linked_lead_id', 
        'partner_center_referrals', ['linked_lead_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_partner_center_referrals_linked_lead_id', 
        table_name='partner_center_referrals')
    op.drop_index('idx_partner_center_referrals_link_status', 
        table_name='partner_center_referrals')
    
    # Drop columns
    op.drop_column('partner_center_referrals', 'linked_lead_id')
    op.drop_column('partner_center_referrals', 'raw_domain')
    op.drop_column('partner_center_referrals', 'link_status')
