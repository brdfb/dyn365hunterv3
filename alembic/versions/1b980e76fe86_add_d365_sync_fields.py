"""add_d365_sync_fields

Revision ID: 1b980e76fe86
Revises: 3cfe9a591887
Create Date: 2025-01-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1b980e76fe86'
down_revision: Union[str, None] = '3cfe9a591887'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add D365 sync fields to companies table (domain-based)
    # Note: Plan says "leads tablosuna" but we use companies table (domain is unique)
    op.add_column('companies', sa.Column('d365_lead_id', sa.String(length=255), nullable=True))
    op.add_column('companies', sa.Column('d365_sync_status', sa.String(length=50), nullable=True, server_default='pending'))
    op.add_column('companies', sa.Column('d365_sync_last_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('companies', sa.Column('d365_sync_error', sa.Text(), nullable=True))
    
    # Create indexes for querying
    op.create_index('idx_companies_d365_sync_status', 'companies', ['d365_sync_status'])
    op.create_index('idx_companies_d365_lead_id', 'companies', ['d365_lead_id'])
    
    # Create d365_push_jobs table for audit trail
    op.create_table(
        'd365_push_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('d365_lead_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_d365_push_jobs_lead_id', 'd365_push_jobs', ['lead_id'])
    op.create_index('idx_d365_push_jobs_status', 'd365_push_jobs', ['status'])
    
    # Update leads_ready view to include D365 sync fields
    op.execute("""
        DROP VIEW IF EXISTS leads_ready CASCADE;
        CREATE VIEW leads_ready AS
        SELECT 
            c.id AS company_id,
            c.canonical_name,
            c.domain,
            c.provider,
            c.tenant_size,
            c.country,
            c.contact_emails,
            c.contact_quality_score,
            c.linkedin_pattern,
            c.updated_at AS company_updated_at,
            c.d365_lead_id,
            c.d365_sync_status,
            c.d365_sync_last_at,
            c.d365_sync_error,
            ds.id AS signal_id,
            ds.spf,
            ds.dkim,
            ds.dmarc_policy,
            ds.dmarc_coverage,
            ds.mx_root,
            ds.local_provider,
            ds.registrar,
            ds.expires_at,
            ds.nameservers,
            ds.scan_status,
            ds.scanned_at,
            ls.id AS score_id,
            ls.readiness_score,
            ls.segment,
            ls.reason,
            ls.technical_heat,
            ls.commercial_segment,
            ls.commercial_heat,
            ls.priority_category,
            ls.priority_label,
            ls.updated_at AS score_updated_at
        FROM companies c
        LEFT JOIN domain_signals ds ON c.domain = ds.domain
        LEFT JOIN lead_scores ls ON c.domain = ls.domain;
    """)


def downgrade() -> None:
    # Restore leads_ready view (without D365 fields)
    op.execute("""
        DROP VIEW IF EXISTS leads_ready CASCADE;
        CREATE VIEW leads_ready AS
        SELECT 
            c.id AS company_id,
            c.canonical_name,
            c.domain,
            c.provider,
            c.tenant_size,
            c.country,
            c.contact_emails,
            c.contact_quality_score,
            c.linkedin_pattern,
            c.updated_at AS company_updated_at,
            ds.id AS signal_id,
            ds.spf,
            ds.dkim,
            ds.dmarc_policy,
            ds.dmarc_coverage,
            ds.mx_root,
            ds.local_provider,
            ds.registrar,
            ds.expires_at,
            ds.nameservers,
            ds.scan_status,
            ds.scanned_at,
            ls.id AS score_id,
            ls.readiness_score,
            ls.segment,
            ls.reason,
            ls.technical_heat,
            ls.commercial_segment,
            ls.commercial_heat,
            ls.priority_category,
            ls.priority_label,
            ls.updated_at AS score_updated_at
        FROM companies c
        LEFT JOIN domain_signals ds ON c.domain = ds.domain
        LEFT JOIN lead_scores ls ON c.domain = ls.domain;
    """)
    
    # Drop d365_push_jobs table
    op.drop_index('idx_d365_push_jobs_status', table_name='d365_push_jobs')
    op.drop_index('idx_d365_push_jobs_lead_id', table_name='d365_push_jobs')
    op.drop_table('d365_push_jobs')
    
    # Drop indexes and columns from companies
    op.drop_index('idx_companies_d365_lead_id', table_name='companies')
    op.drop_index('idx_companies_d365_sync_status', table_name='companies')
    op.drop_column('companies', 'd365_sync_error')
    op.drop_column('companies', 'd365_sync_last_at')
    op.drop_column('companies', 'd365_sync_status')
    op.drop_column('companies', 'd365_lead_id')
