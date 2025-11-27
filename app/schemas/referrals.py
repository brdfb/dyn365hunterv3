"""Partner Center referral schemas (Phase 2)."""

from typing import Any, Dict, List, Optional
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


class ReferralContactInfo(BaseModel):
    """Contact information for referral detail view."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None


class ReferralTeamMember(BaseModel):
    """Team member info from customerProfile.team."""

    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None


class ReferralDealInfo(BaseModel):
    """Deal details from referral."""

    lead_name: Optional[str] = None
    lead_id: Optional[str] = None
    estimated_close_date: Optional[str] = None
    estimated_value: Optional[float] = None
    currency: Optional[str] = None
    notes: Optional[str] = None


class ReferralDetailResponse(BaseModel):
    """Detailed Partner Center referral response for modal view."""

    referral_id: str
    referral_type: Optional[str] = None
    status: Optional[str] = None
    substatus: Optional[str] = None
    direction: Optional[str] = None
    link_status: Optional[str] = None
    company_name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_country: Optional[str] = None
    organization_size: Optional[str] = None
    domain: Optional[str] = None
    raw_domain: Optional[str] = None
    deal_value: Optional[float] = None
    currency: Optional[str] = None
    synced_at: Optional[str] = None

    contact: ReferralContactInfo
    deal: ReferralDealInfo
    team_members: List[ReferralTeamMember] = []

    raw_data: Optional[Dict[str, Any]] = None

