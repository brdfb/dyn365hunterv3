"""add_partner_center_referrals

Revision ID: 622ba66483b9
Revises: e7196f7e556b
Create Date: 2025-01-28 14:00:00.000000

NOTES:
- Adds partner_center_referrals table for Partner Center referral lifecycle tracking
- Feature flag: PARTNER_CENTER_ENABLED (default: false)
- Hybrid model: raw_leads ingestion + partner_center_referrals tracking
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '622ba66483b9'
down_revision: Union[str, None] = 'e7196f7e556b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create partner_center_referrals table
    op.create_table(
        'partner_center_referrals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('referral_id', sa.String(length=255), nullable=False),  # Partner Center referral ID (UNIQUE)
        sa.Column('referral_type', sa.String(length=50), nullable=True),  # 'co-sell', 'marketplace', 'solution-provider'
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=True),  # Normalized domain
        sa.Column('azure_tenant_id', sa.String(length=255), nullable=True),  # Azure Tenant ID (M365 signal)
        sa.Column('status', sa.String(length=50), nullable=True),  # Referral status
        sa.Column('raw_data', postgresql.JSONB(), nullable=True),  # Full referral data from Partner Center
        sa.Column('synced_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create unique constraint on referral_id
    op.create_unique_constraint('uq_partner_center_referrals_referral_id', 'partner_center_referrals', ['referral_id'])
    
    # Create indexes
    op.create_index(op.f('ix_partner_center_referrals_referral_id'), 'partner_center_referrals', ['referral_id'], unique=True)
    op.create_index('idx_partner_center_referrals_domain', 'partner_center_referrals', ['domain'], unique=False)
    op.create_index('idx_partner_center_referrals_status', 'partner_center_referrals', ['status'], unique=False)
    op.create_index('idx_partner_center_referrals_synced_at', 'partner_center_referrals', ['synced_at'], unique=False)
    op.create_index('idx_partner_center_referrals_type', 'partner_center_referrals', ['referral_type'], unique=False)
    op.create_index('idx_partner_center_referrals_tenant_id', 'partner_center_referrals', ['azure_tenant_id'], unique=False)
    
    # Add table comment
    op.create_table_comment(
        'partner_center_referrals',
        'Partner Center referral lifecycle tracking',
        existing_comment=None,
        schema=None
    )


def downgrade() -> None:
    # Drop table
    op.drop_table_comment('partner_center_referrals', existing_comment='Partner Center referral lifecycle tracking', schema=None)
    op.drop_index('idx_partner_center_referrals_tenant_id', table_name='partner_center_referrals')
    op.drop_index('idx_partner_center_referrals_type', table_name='partner_center_referrals')
    op.drop_index('idx_partner_center_referrals_synced_at', table_name='partner_center_referrals')
    op.drop_index('idx_partner_center_referrals_status', table_name='partner_center_referrals')
    op.drop_index('idx_partner_center_referrals_domain', table_name='partner_center_referrals')
    op.drop_index(op.f('ix_partner_center_referrals_referral_id'), table_name='partner_center_referrals')
    op.drop_constraint('uq_partner_center_referrals_referral_id', 'partner_center_referrals', type_='unique')
    op.drop_table('partner_center_referrals')

