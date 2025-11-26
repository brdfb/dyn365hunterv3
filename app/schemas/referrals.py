"""Partner Center referral schemas (Phase 2)."""

from typing import List, Optional
from pydantic import BaseModel


class ReferralInboxItem(BaseModel):
    """Single referral item in inbox response."""

    id: int
    referral_id: str
    company_name: Optional[str] = None
    customer_name: Optional[str] = None
    domain: Optional[str] = None
    raw_domain: Optional[str] = None
    referral_type: Optional[str] = None  # 'co-sell' | 'marketplace' | 'solution-provider'
    status: Optional[str] = None
    substatus: Optional[str] = None
    link_status: Optional[str] = None  # 'auto_linked' | 'unlinked' | 'multi_candidate'
    linked_lead_id: Optional[int] = None
    deal_value: Optional[float] = None
    currency: Optional[str] = None
    synced_at: Optional[str] = None  # ISO string

    class Config:
        from_attributes = True


class ReferralInboxResponse(BaseModel):
    """Response model for referral inbox list."""

    referrals: List[ReferralInboxItem]
    total: int
    page: int
    page_size: int


class LinkReferralRequest(BaseModel):
    """Request model for linking referral to existing lead."""

    lead_domain: str


class LinkReferralResponse(BaseModel):
    """Response model for link referral action."""

    status: str
    lead_id: int
    domain: str


class CreateLeadFromReferralRequest(BaseModel):
    """Request model for creating lead from referral."""

    company_name_override: Optional[str] = None
    notes: Optional[str] = None


class CreateLeadFromReferralResponse(BaseModel):
    """Response model for create lead from referral action."""

    status: str
    lead_id: int
    domain: str

