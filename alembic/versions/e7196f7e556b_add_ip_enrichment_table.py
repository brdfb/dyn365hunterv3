"""add_ip_enrichment_table

Revision ID: e7196f7e556b
Revises: 08f51db8dce0
Create Date: 2025-01-28 12:00:00.000000

NOTES:
- Adds ip_enrichment table for IP geolocation, ASN, and proxy detection
- Feature flag: ENRICHMENT_ENABLED (default: false)
- Requires MaxMind GeoLite2 and/or IP2Location/IP2Proxy DB files
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e7196f7e556b'
down_revision: Union[str, None] = '08f51db8dce0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ip_enrichment table
    op.create_table(
        'ip_enrichment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),  # IPv4 or IPv6
        sa.Column('asn', sa.Integer(), nullable=True),  # Autonomous System Number
        sa.Column('asn_org', sa.String(length=255), nullable=True),  # ASN Organization
        sa.Column('isp', sa.String(length=255), nullable=True),  # Internet Service Provider
        sa.Column('country', sa.String(length=2), nullable=True),  # ISO 3166-1 alpha-2
        sa.Column('city', sa.String(length=255), nullable=True),
        sa.Column('usage_type', sa.String(length=32), nullable=True),  # DCH, COM, RES, MOB
        sa.Column('is_proxy', sa.Boolean(), nullable=True),  # Proxy detection
        sa.Column('proxy_type', sa.String(length=32), nullable=True),  # VPN, TOR, PUB
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['domain'], ['companies.domain'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_ip_enrichment_domain'), 'ip_enrichment', ['domain'], unique=False)
    op.create_index(op.f('ix_ip_enrichment_ip'), 'ip_enrichment', ['ip_address'], unique=False)
    
    # Create unique constraint (domain, ip_address) for UPSERT support
    op.create_unique_constraint('uq_ip_enrichment_domain_ip', 'ip_enrichment', ['domain', 'ip_address'])
    
    # Add table comment
    op.create_table_comment(
        'ip_enrichment',
        'IP enrichment data for domains (IP geolocation, ASN, proxy detection)',
        existing_comment=None,
        schema=None
    )


def downgrade() -> None:
    # Drop table (cascade will handle foreign keys)
    op.drop_table_comment('ip_enrichment', existing_comment='IP enrichment data for domains (IP geolocation, ASN, proxy detection)', schema=None)
    op.drop_constraint('uq_ip_enrichment_domain_ip', 'ip_enrichment', type_='unique')
    op.drop_index(op.f('ix_ip_enrichment_ip'), table_name='ip_enrichment')
    op.drop_index(op.f('ix_ip_enrichment_domain'), table_name='ip_enrichment')
    op.drop_table('ip_enrichment')

