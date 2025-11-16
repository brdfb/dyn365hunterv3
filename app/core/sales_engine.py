"""Sales intelligence engine for generating sales insights and recommendations."""

from typing import Dict, List, Optional, Any
from datetime import datetime, date


def generate_one_liner(
    domain: str,
    provider: Optional[str],
    segment: Optional[str],
    readiness_score: Optional[int],
    tenant_size: Optional[str],
    local_provider: Optional[str] = None,
    ip_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate a 1-sentence sales summary for a lead.

    Args:
        domain: Domain name
        provider: Provider name (M365, Google, Local, etc.)
        segment: Lead segment (Migration, Existing, Cold, Skip)
        readiness_score: Readiness score (0-100)
        tenant_size: Tenant size (small, medium, large)
        local_provider: Local provider name (e.g., TürkHost, Natro)

    Returns:
        One-sentence sales summary
    """
    if not domain:
        return "Domain bilgisi eksik."

    # IP context integration (optional, for intelligent text generation)
    ip_country = ip_context.get("country") if ip_context else None
    ip_is_proxy = ip_context.get("is_proxy") if ip_context else None

    # Migration segment - highest priority
    if segment == "Migration":
        if readiness_score and readiness_score >= 80:
            country_note = f" ({ip_country} merkezli)" if ip_country else ""
            proxy_warning = " ⚠️ Proxy altyapısı tespit edildi, dikkatli değerlendirme gerekli." if ip_is_proxy else ""
            if tenant_size == "large":
                return f"{domain} - Büyük ölçekli migration fırsatı{country_note}, yüksek hazırlık skoru ({readiness_score}), Enterprise teklif hazırlanabilir.{proxy_warning}"
            elif tenant_size == "medium":
                return f"{domain} - Orta ölçekli migration fırsatı{country_note}, yüksek hazırlık skoru ({readiness_score}), Business Standard teklif hazırlanabilir.{proxy_warning}"
            elif tenant_size == "small":
                return f"{domain} - Küçük ölçekli migration fırsatı{country_note}, yüksek hazırlık skoru ({readiness_score}), Business Basic teklif hazırlanabilir.{proxy_warning}"
            else:
                return f"{domain} - Migration fırsatı{country_note}, yüksek hazırlık skoru ({readiness_score}), hemen aksiyon alınabilir.{proxy_warning}"
        elif readiness_score and readiness_score >= 50:
            if local_provider:
                return f"{domain} - {local_provider} kullanıyor, migration fırsatı (skor: {readiness_score}), takip edilmeli."
            return f"{domain} - Migration fırsatı, orta hazırlık skoru ({readiness_score}), takip edilmeli."
        else:
            if local_provider:
                return f"{domain} - {local_provider} kullanıyor, migration potansiyeli var (skor: {readiness_score}), uzun vadeli takip."
            return f"{domain} - Migration potansiyeli var, düşük hazırlık skoru ({readiness_score}), uzun vadeli takip."

    # Existing segment - upsell opportunity
    elif segment == "Existing":
        if readiness_score and readiness_score >= 70:
            return f"{domain} - Mevcut müşteri, yüksek skor ({readiness_score}), Defender veya ek güvenlik çözümleri için upsell fırsatı."
        elif readiness_score and readiness_score >= 50:
            return f"{domain} - Mevcut müşteri, orta skor ({readiness_score}), güvenlik iyileştirmeleri için takip edilmeli."
        else:
            return f"{domain} - Mevcut müşteri, düşük skor ({readiness_score}), uzun vadeli iyileştirme fırsatı."

    # Cold segment - low priority
    elif segment == "Cold":
        if readiness_score and readiness_score >= 40:
            return f"{domain} - Soğuk lead, orta skor ({readiness_score}), uzun vadeli takip edilebilir."
        else:
            return f"{domain} - Soğuk lead, düşük skor ({readiness_score}), düşük öncelik."

    # Skip segment - lowest priority
    else:
        return f"{domain} - Skip segmenti, şu an için takip edilmemeli."


def generate_call_script(
    domain: str,
    provider: Optional[str],
    segment: Optional[str],
    readiness_score: Optional[int],
    tenant_size: Optional[str],
    local_provider: Optional[str] = None,
    spf: Optional[bool] = None,
    dkim: Optional[bool] = None,
    dmarc_policy: Optional[str] = None,
    dmarc_coverage: Optional[int] = None,
    ip_context: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Generate call script bullets for sales outreach.

    Args:
        domain: Domain name
        provider: Provider name (M365, Google, Local, etc.)
        segment: Lead segment (Migration, Existing, Cold, Skip)
        readiness_score: Readiness score (0-100)
        tenant_size: Tenant size (small, medium, large)
        local_provider: Local provider name (e.g., TürkHost, Natro)
        spf: SPF record exists
        dkim: DKIM record exists
        dmarc_policy: DMARC policy (none, quarantine, reject)
        dmarc_coverage: DMARC coverage percentage (0-100)

    Returns:
        List of call script bullets
    """
    bullets = []

    # IP context integration (optional, for intelligent text generation)
    ip_country = ip_context.get("country") if ip_context else None
    ip_is_proxy = ip_context.get("is_proxy") if ip_context else None
    ip_city = ip_context.get("city") if ip_context else None

    # Opening line based on segment
    if segment == "Migration":
        country_note = f" ({ip_country} merkezli)" if ip_country else ""
        if local_provider:
            bullets.append(
                f"Merhaba, {domain} için email altyapınızı inceledik{country_note}. Şu anda {local_provider} kullanıyorsunuz ve Microsoft 365'e geçiş için uygun bir fırsat görüyoruz."
            )
        else:
            bullets.append(
                f"Merhaba, {domain} için email altyapınızı inceledik{country_note} ve Microsoft 365'e geçiş için uygun bir fırsat görüyoruz."
            )
        
        # Proxy warning if detected
        if ip_is_proxy:
            bullets.append(
                "⚠️ Not: E-posta altyapınızın proxy üzerinden yönlendirildiğini tespit ettik. Bu durum geçiş sürecinde dikkate alınmalıdır."
            )
    elif segment == "Existing":
        bullets.append(
            f"Merhaba, {domain} için mevcut Microsoft 365 altyapınızı inceledik ve güvenlik iyileştirmeleri için önerilerimiz var."
        )
    else:
        bullets.append(
            f"Merhaba, {domain} için email güvenliği ve altyapı analizi yaptık ve sizinle paylaşmak istediğimiz önemli bulgular var."
        )

    # Security signals
    security_issues = []
    if spf is False:
        security_issues.append("SPF kaydı eksik")
    if dkim is False:
        security_issues.append("DKIM kaydı eksik")
    if dmarc_policy == "none" or dmarc_policy is None:
        security_issues.append("DMARC politikası yok")
    elif dmarc_policy in ["quarantine", "reject"] and dmarc_coverage and dmarc_coverage < 100:
        security_issues.append(f"DMARC kapsamı sadece %{dmarc_coverage}")

    if security_issues:
        bullets.append(
            f"Güvenlik analizi: {', '.join(security_issues)}. Bu durum email spoofing ve phishing saldırılarına karşı risk oluşturuyor."
        )

    # Value proposition based on segment
    if segment == "Migration":
        if tenant_size == "large":
            bullets.append(
                "Enterprise çözümümüz ile büyük ölçekli migration yapabilir, IT maliyetlerinizi düşürebilir ve güvenliği artırabiliriz."
            )
        elif tenant_size == "medium":
            bullets.append(
                "Business Standard çözümümüz ile orta ölçekli migration yapabilir, mail deliverability'yi %40 artırabiliriz."
            )
        elif tenant_size == "small":
            bullets.append(
                "Business Basic çözümümüz ile küçük ölçekli migration yapabilir, maliyet-etkin bir geçiş sağlayabiliriz."
            )
        else:
            bullets.append(
                "Microsoft 365'e geçiş ile mail deliverability'yi artırabilir, güvenliği iyileştirebilir ve IT maliyetlerinizi düşürebiliriz."
            )
    elif segment == "Existing":
        bullets.append(
            "Microsoft Defender for Office 365 ve ek güvenlik çözümlerimiz ile mevcut altyapınızı güçlendirebiliriz."
        )

    # Call to action
    if segment == "Migration" and readiness_score and readiness_score >= 70:
        bullets.append(
            "15 dakikalık kısa bir görüşme yapabilir miyiz? Size özel bir teklif hazırlayabilirim."
        )
    elif segment == "Existing":
        bullets.append(
            "Mevcut altyapınızı değerlendirmek için kısa bir görüşme yapabilir miyiz?"
        )
    else:
        bullets.append(
            "Detaylı analiz sonuçlarını paylaşmak için kısa bir görüşme yapabilir miyiz?"
        )

    return bullets


def generate_discovery_questions(
    segment: Optional[str],
    provider: Optional[str],
    tenant_size: Optional[str],
) -> List[str]:
    """
    Generate discovery questions for sales qualification.

    Args:
        segment: Lead segment (Migration, Existing, Cold, Skip)
        provider: Provider name (M365, Google, Local, etc.)
        tenant_size: Tenant size (small, medium, large)

    Returns:
        List of discovery questions
    """
    questions = []

    # Segment-specific questions
    if segment == "Migration":
        questions.append("Şu anki email altyapınızdan memnun musunuz? Hangi zorluklarla karşılaşıyorsunuz?")
        questions.append("Email güvenliği konusunda endişeleriniz var mı? Son dönemde phishing veya spam sorunları yaşadınız mı?")
        questions.append("IT ekibinizin büyüklüğü nedir? Email yönetimi için ne kadar zaman harcıyorsunuz?")
        if provider == "Local":
            questions.append("Local hosting sağlayıcınızdan memnun musunuz? Ölçeklenebilirlik ve güvenlik konusunda endişeleriniz var mı?")
    elif segment == "Existing":
        questions.append("Mevcut Microsoft 365 altyapınızdan memnun musunuz? Hangi özellikleri kullanıyorsunuz?")
        questions.append("Güvenlik konusunda ek ihtiyaçlarınız var mı? Defender veya ek güvenlik çözümleri düşünüyor musunuz?")
        questions.append("Email deliverability konusunda sorunlar yaşıyor musunuz? Spam klasörüne düşme oranınız nedir?")
    else:
        questions.append("Email altyapınız hakkında genel olarak ne düşünüyorsunuz?")
        questions.append("Güvenlik ve email yönetimi konusunda öncelikleriniz neler?")

    # Tenant size-specific questions
    if tenant_size == "large":
        questions.append("Büyük ölçekli bir organizasyonsunuz. Email yönetimi ve güvenlik için merkezi bir stratejiniz var mı?")
        questions.append("Compliance ve regülasyon gereksinimleriniz neler? (GDPR, KVKK, vb.)")
    elif tenant_size == "medium":
        questions.append("Orta ölçekli bir organizasyonsunuz. Büyüme planlarınız var mı? Email altyapınız büyümeye hazır mı?")
    elif tenant_size == "small":
        questions.append("Küçük ölçekli bir organizasyonsunuz. Email yönetimi için ne kadar bütçe ayırıyorsunuz?")

    # Budget and timeline questions
    questions.append("Email altyapısı için yıllık bütçeniz nedir?")
    questions.append("Bu konuda karar verme süreciniz nasıl işliyor? Kimler dahil oluyor?")
    questions.append("Zaman çizelgeniz nedir? Acil bir ihtiyaç var mı yoksa planlama aşamasında mısınız?")

    return questions


def recommend_offer_tier(
    tenant_size: Optional[str],
    segment: Optional[str],
    readiness_score: Optional[int],
) -> Dict[str, Any]:
    """
    Recommend offer tier (Basic/Pro/Enterprise) based on tenant size and segment.

    Args:
        tenant_size: Tenant size (small, medium, large)
        segment: Lead segment (Migration, Existing, Cold, Skip)
        readiness_score: Readiness score (0-100)

    Returns:
        Dictionary with tier recommendation and details
    """
    if tenant_size == "large":
        return {
            "tier": "Enterprise",
            "license": "Enterprise",
            "price_per_user_per_month": 20,  # €20/kullanıcı/ay
            "migration_fee": 10000,  # €10,000
            "defender_price_per_user_per_month": 10,  # €10/kullanıcı/ay
            "consulting_fee": 50000,  # €50,000
            "recommendation": "Enterprise çözümü önerilir. Büyük ölçekli organizasyonlar için Defender ve Consulting hizmetleri dahil.",
        }
    elif tenant_size == "medium":
        return {
            "tier": "Business Standard",
            "license": "Business Standard",
            "price_per_user_per_month": 10,  # €10/kullanıcı/ay
            "migration_fee": 2000,  # €2,000
            "defender_price_per_user_per_month": 5,  # €5/kullanıcı/ay
            "consulting_fee": None,
            "recommendation": "Business Standard çözümü önerilir. Orta ölçekli organizasyonlar için Defender opsiyonel.",
        }
    elif tenant_size == "small":
        return {
            "tier": "Business Basic",
            "license": "Business Basic",
            "price_per_user_per_month": 5,  # €5/kullanıcı/ay
            "migration_fee": 500,  # €500
            "defender_price_per_user_per_month": None,
            "consulting_fee": None,
            "recommendation": "Business Basic çözümü önerilir. Küçük ölçekli organizasyonlar için maliyet-etkin çözüm.",
        }
    else:
        # Default recommendation based on segment
        if segment == "Migration" and readiness_score and readiness_score >= 70:
            return {
                "tier": "Business Standard",
                "license": "Business Standard",
                "price_per_user_per_month": 10,
                "migration_fee": 2000,
                "defender_price_per_user_per_month": 5,
                "consulting_fee": None,
                "recommendation": "Business Standard çözümü önerilir. Yüksek hazırlık skoru nedeniyle orta ölçekli çözüm uygun.",
            }
        else:
            return {
                "tier": "Business Basic",
                "license": "Business Basic",
                "price_per_user_per_month": 5,
                "migration_fee": 500,
                "defender_price_per_user_per_month": None,
                "consulting_fee": None,
                "recommendation": "Business Basic çözümü önerilir. Başlangıç için maliyet-etkin çözüm.",
            }


def calculate_opportunity_potential(
    segment: Optional[str],
    readiness_score: Optional[int],
    priority_score: Optional[int],
    tenant_size: Optional[str],
    contact_quality_score: Optional[int] = None,
    tuning_factor: float = 1.0,
) -> int:
    """
    Calculate opportunity potential score (0-100).

    Args:
        segment: Lead segment (Migration, Existing, Cold, Skip)
        readiness_score: Readiness score (0-100)
        priority_score: Priority score (1-7, 1 is highest)
        tenant_size: Tenant size (small, medium, large)
        contact_quality_score: Contact quality score (0-100)

    Returns:
        Opportunity potential score (0-100)
    """
    score = 0

    # Segment weight (40 points)
    if segment == "Migration":
        score += 40
    elif segment == "Existing":
        score += 30
    elif segment == "Cold":
        score += 15
    else:  # Skip
        score += 5

    # Readiness score weight (30 points)
    if readiness_score:
        score += int(readiness_score * 0.3)
    else:
        score += 10  # Default if no score

    # Priority score weight (20 points) - inverse (lower priority_score = higher opportunity)
    if priority_score:
        if priority_score == 1:
            score += 20
        elif priority_score == 2:
            score += 18
        elif priority_score == 3:
            score += 15
        elif priority_score == 4:
            score += 12
        elif priority_score == 5:
            score += 8
        elif priority_score == 6:
            score += 5
        else:  # 7
            score += 2
    else:
        score += 5  # Default

    # Tenant size weight (10 points)
    if tenant_size == "large":
        score += 10
    elif tenant_size == "medium":
        score += 7
    elif tenant_size == "small":
        score += 5
    else:
        score += 3  # Unknown

    # Contact quality bonus (optional, up to 5 points)
    if contact_quality_score:
        score += int(contact_quality_score * 0.05)

    # Apply tuning factor (from config, default: 1.0)
    # Allows fine-tuning: 0.9 = 10% reduction, 1.1 = 10% increase
    score = int(score * tuning_factor)

    # Cap at 100
    return min(score, 100)


def calculate_urgency(
    segment: Optional[str],
    priority_score: Optional[int],
    readiness_score: Optional[int],
    expires_at: Optional[date] = None,
) -> str:
    """
    Calculate urgency level (low/medium/high).

    Args:
        segment: Lead segment (Migration, Existing, Cold, Skip)
        priority_score: Priority score (1-7, 1 is highest)
        readiness_score: Readiness score (0-100)
        expires_at: Domain expiration date

    Returns:
        Urgency level: "high", "medium", or "low"
    """
    # High urgency conditions
    if priority_score == 1:
        return "high"
    if segment == "Migration" and readiness_score and readiness_score >= 80:
        return "high"
    if expires_at:
        days_until_expiry = (expires_at - date.today()).days
        if days_until_expiry < 60:
            return "high"

    # Medium urgency conditions
    if priority_score == 2:
        return "medium"
    if segment == "Migration" and readiness_score and readiness_score >= 50:
        return "medium"
    if segment == "Existing" and readiness_score and readiness_score >= 70:
        return "medium"
    if expires_at:
        days_until_expiry = (expires_at - date.today()).days
        if 60 <= days_until_expiry < 90:
            return "medium"
        if days_until_expiry >= 90:
            # Far expiry doesn't override low priority
            if priority_score and priority_score >= 4:
                return "low"

    # Low urgency (default)
    return "low"


def generate_sales_summary(
    domain: str,
    provider: Optional[str],
    segment: Optional[str],
    readiness_score: Optional[int],
    priority_score: Optional[int],
    tenant_size: Optional[str],
    local_provider: Optional[str] = None,
    spf: Optional[bool] = None,
    dkim: Optional[bool] = None,
    dmarc_policy: Optional[str] = None,
    dmarc_coverage: Optional[int] = None,
    contact_quality_score: Optional[int] = None,
    expires_at: Optional[date] = None,
    tuning_factor: float = 1.0,
    ip_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate complete sales intelligence summary.

    Args:
        domain: Domain name
        provider: Provider name (M365, Google, Local, etc.)
        segment: Lead segment (Migration, Existing, Cold, Skip)
        readiness_score: Readiness score (0-100)
        priority_score: Priority score (1-7, 1 is highest)
        tenant_size: Tenant size (small, medium, large)
        local_provider: Local provider name (e.g., TürkHost, Natro)
        spf: SPF record exists
        dkim: DKIM record exists
        dmarc_policy: DMARC policy (none, quarantine, reject)
        dmarc_coverage: DMARC coverage percentage (0-100)
        contact_quality_score: Contact quality score (0-100)
        expires_at: Domain expiration date
        ip_context: Optional IP enrichment context dict with:
            - country: Optional[str] - ISO 3166-1 alpha-2 country code
            - is_proxy: Optional[bool] - Proxy detection result
            - proxy_type: Optional[str] - Proxy type (VPN, TOR, PUB, etc.)

    Returns:
        Complete sales intelligence summary dictionary
    """
    return {
        "domain": domain,
        "one_liner": generate_one_liner(
            domain, provider, segment, readiness_score, tenant_size, local_provider, ip_context
        ),
        "call_script": generate_call_script(
            domain,
            provider,
            segment,
            readiness_score,
            tenant_size,
            local_provider,
            spf,
            dkim,
            dmarc_policy,
            dmarc_coverage,
            ip_context,
        ),
        "discovery_questions": generate_discovery_questions(
            segment, provider, tenant_size
        ),
        "offer_tier": recommend_offer_tier(tenant_size, segment, readiness_score),
        "opportunity_potential": calculate_opportunity_potential(
            segment, readiness_score, priority_score, tenant_size, contact_quality_score, tuning_factor
        ),
        "urgency": calculate_urgency(segment, priority_score, readiness_score, expires_at),
        "metadata": {
            "domain": domain,
            "provider": provider,
            "segment": segment,
            "readiness_score": readiness_score,
            "priority_score": priority_score,
            "tenant_size": tenant_size,
            "local_provider": local_provider,
            "generated_at": datetime.now().isoformat(),
        },
    }

