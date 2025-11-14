"""Auto-tagging logic for domains based on signals and scores (G17)."""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.models import Tag, DomainSignal, LeadScore, Company


def apply_auto_tags(domain: str, db: Session) -> List[str]:
    """
    Apply auto-tags to a domain based on its signals and scores.
    
    Auto-tagging rules:
    - "security-risk": no SPF + no DKIM
    - "migration-ready": Migration segment + score >= 70
    - "expire-soon": expires_at < 30 days
    - "weak-spf": SPF exists but weak (DMARC policy is 'none')
    - "google-workspace": provider = Google
    - "local-mx": provider = Local
    
    Args:
        domain: Domain name
        db: Database session
        
    Returns:
        List of tags that were applied
    """
    applied_tags = []
    
    # Get domain signals
    domain_signal = db.query(DomainSignal).filter(DomainSignal.domain == domain).first()
    
    # Get lead score
    lead_score = db.query(LeadScore).filter(LeadScore.domain == domain).first()
    
    # Get company
    company = db.query(Company).filter(Company.domain == domain).first()
    
    if not domain_signal or not lead_score:
        # Can't auto-tag without signals and scores
        return applied_tags
    
    # Check for security-risk: no SPF + no DKIM
    if domain_signal.spf is False and domain_signal.dkim is False:
        tag_name = "security-risk"
        if not _tag_exists(domain, tag_name, db):
            tag = Tag(domain=domain, tag=tag_name)
            db.add(tag)
            applied_tags.append(tag_name)
    
    # Check for migration-ready: Migration segment + score >= 70
    if lead_score.segment == "Migration" and lead_score.readiness_score >= 70:
        tag_name = "migration-ready"
        if not _tag_exists(domain, tag_name, db):
            tag = Tag(domain=domain, tag=tag_name)
            db.add(tag)
            applied_tags.append(tag_name)
    
    # Check for expire-soon: expires_at < 30 days
    if domain_signal.expires_at:
        days_until_expiry = (domain_signal.expires_at - datetime.now().date()).days
        if 0 < days_until_expiry < 30:
            tag_name = "expire-soon"
            if not _tag_exists(domain, tag_name, db):
                tag = Tag(domain=domain, tag=tag_name)
                db.add(tag)
                applied_tags.append(tag_name)
    
    # Check for weak-spf: SPF exists but DMARC policy is 'none'
    if domain_signal.spf is True and domain_signal.dmarc_policy == "none":
        tag_name = "weak-spf"
        if not _tag_exists(domain, tag_name, db):
            tag = Tag(domain=domain, tag=tag_name)
            db.add(tag)
            applied_tags.append(tag_name)
    
    # Check for google-workspace: provider = Google
    if company and company.provider == "Google":
        tag_name = "google-workspace"
        if not _tag_exists(domain, tag_name, db):
            tag = Tag(domain=domain, tag=tag_name)
            db.add(tag)
            applied_tags.append(tag_name)
    
    # Check for local-mx: provider = Local
    if company and company.provider == "Local":
        tag_name = "local-mx"
        if not _tag_exists(domain, tag_name, db):
            tag = Tag(domain=domain, tag=tag_name)
            db.add(tag)
            applied_tags.append(tag_name)
    
    return applied_tags


def _tag_exists(domain: str, tag_name: str, db: Session) -> bool:
    """Check if a tag already exists for a domain."""
    existing = db.query(Tag).filter(
        Tag.domain == domain,
        Tag.tag == tag_name
    ).first()
    return existing is not None

