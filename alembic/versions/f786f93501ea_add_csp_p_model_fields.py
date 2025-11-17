"""add_csp_p_model_fields

Revision ID: f786f93501ea
Revises: 622ba66483b9
Create Date: 2025-11-17 19:33:06.937894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f786f93501ea'
down_revision: Union[str, None] = '622ba66483b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add CSP P-Model fields to lead_scores table
    op.add_column('lead_scores', sa.Column('technical_heat', sa.String(length=20), nullable=True))
    op.add_column('lead_scores', sa.Column('commercial_segment', sa.String(length=50), nullable=True))
    op.add_column('lead_scores', sa.Column('commercial_heat', sa.String(length=20), nullable=True))
    op.add_column('lead_scores', sa.Column('priority_category', sa.String(length=10), nullable=True))
    op.add_column('lead_scores', sa.Column('priority_label', sa.String(length=100), nullable=True))
    
    # Create indexes for filtering and querying
    op.create_index('idx_lead_scores_technical_heat', 'lead_scores', ['technical_heat'])
    op.create_index('idx_lead_scores_commercial_segment', 'lead_scores', ['commercial_segment'])
    op.create_index('idx_lead_scores_commercial_heat', 'lead_scores', ['commercial_heat'])
    op.create_index('idx_lead_scores_priority_category', 'lead_scores', ['priority_category'])
    
    # Update leads_ready view to include new CSP P-Model fields
    # Check which columns exist before creating view
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    
    companies_columns = [col['name'] for col in inspector.get_columns('companies')]
    domain_signals_columns = [col['name'] for col in inspector.get_columns('domain_signals')]
    
    # Build SELECT clause dynamically based on available columns
    select_parts = [
        "c.id AS company_id",
        "c.canonical_name",
        "c.domain",
        "c.provider",
    ]
    
    if 'tenant_size' in companies_columns:
        select_parts.append("c.tenant_size")
    
    select_parts.extend([
        "c.country",
        "c.contact_emails",
        "c.contact_quality_score",
        "c.linkedin_pattern",
        "c.updated_at AS company_updated_at",
        "ds.id AS signal_id",
        "ds.spf",
        "ds.dkim",
        "ds.dmarc_policy",
    ])
    
    if 'dmarc_coverage' in domain_signals_columns:
        select_parts.append("ds.dmarc_coverage")
    
    select_parts.extend([
        "ds.mx_root",
    ])
    
    if 'local_provider' in domain_signals_columns:
        select_parts.append("ds.local_provider")
    
    select_parts.extend([
        "ds.registrar",
        "ds.expires_at",
        "ds.nameservers",
        "ds.scan_status",
        "ds.scanned_at",
        "ls.id AS score_id",
        "ls.readiness_score",
        "ls.segment",
        "ls.reason",
        "ls.technical_heat",
        "ls.commercial_segment",
        "ls.commercial_heat",
        "ls.priority_category",
        "ls.priority_label",
        "ls.updated_at AS score_updated_at"
    ])
    
    view_sql = f"""
        DROP VIEW IF EXISTS leads_ready CASCADE;
        CREATE VIEW leads_ready AS
        SELECT 
            {', '.join(select_parts)}
        FROM companies c
        LEFT JOIN domain_signals ds ON c.domain = ds.domain
        LEFT JOIN lead_scores ls ON c.domain = ls.domain;
    """
    
    op.execute(view_sql)


def downgrade() -> None:
    # Restore original leads_ready view (without CSP P-Model fields)
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
            ls.updated_at AS score_updated_at
        FROM companies c
        LEFT JOIN domain_signals ds ON c.domain = ds.domain
        LEFT JOIN lead_scores ls ON c.domain = ls.domain;
    """)
    
    # Drop indexes first
    op.drop_index('idx_lead_scores_priority_category', table_name='lead_scores')
    op.drop_index('idx_lead_scores_commercial_heat', table_name='lead_scores')
    op.drop_index('idx_lead_scores_commercial_segment', table_name='lead_scores')
    op.drop_index('idx_lead_scores_technical_heat', table_name='lead_scores')
    
    # Drop columns
    op.drop_column('lead_scores', 'priority_label')
    op.drop_column('lead_scores', 'priority_category')
    op.drop_column('lead_scores', 'commercial_heat')
    op.drop_column('lead_scores', 'commercial_segment')
    op.drop_column('lead_scores', 'technical_heat')
