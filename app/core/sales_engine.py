"""Sales intelligence engine for generating sales insights and recommendations."""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
import json
from pathlib import Path


def explain_segment(
    segment: Optional[str],
    provider: Optional[str],
    readiness_score: Optional[int],
    local_provider: Optional[str] = None,
    spf: Optional[bool] = None,
    dkim: Optional[bool] = None,
    dmarc_policy: Optional[str] = None,
) -> str:
    """
    Generate AI explanation for why a lead is in a specific segment.
    
    Args:
        segment: Lead segment (Migration, Existing, Cold, Skip)
        provider: Provider name (M365, Google, Local, etc.)
        readiness_score: Readiness score (0-100)
        local_provider: Local provider name (e.g., TürkHost, Natro)
        spf: SPF record exists
        dkim: DKIM record exists
        dmarc_policy: DMARC policy (none, quarantine, reject)
    
    Returns:
        Human-readable explanation of why the lead is in this segment
    """
    if not segment:
        return "Segment bilgisi mevcut değil."
    
    # Load segment rules to understand the logic
    current_dir = Path(__file__).parent.parent
    rules_path = current_dir / "data" / "rules.json"
    
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            rules = json.load(f)
        segment_rules = rules.get("segment_rules", [])
    except (FileNotFoundError, json.JSONDecodeError):
        segment_rules = []
    
    # Find matching rule for explanation
    matching_rule = None
    for rule in segment_rules:
        if rule.get("segment") == segment:
            condition = rule.get("condition", {})
            # Check if this rule matches
            min_score = condition.get("min_score")
            max_score = condition.get("max_score")
            provider_in = condition.get("provider_in")
            
            # Check score range
            if readiness_score is not None:
                if min_score is not None and readiness_score < min_score:
                    continue
                if max_score is not None and readiness_score > max_score:
                    continue
            elif min_score is not None:
                continue
            
            # Check provider
            if provider_in is not None:
                if provider not in provider_in:
                    continue
            
            matching_rule = rule
            break
    
    # Generate explanation based on segment
    if segment == "Existing":
        if provider == "M365":
            explanation = f"Bu lead **Existing** segmentinde çünkü: "
            explanation += f"Microsoft 365 (M365) kullanıyor. "
            if readiness_score is not None:
                if readiness_score >= 70:
                    explanation += f"Yüksek hazırlık skoru ({readiness_score}) ile mevcut müşteri, "
                    explanation += "Defender veya ek güvenlik çözümleri için upsell fırsatı var."
                elif readiness_score >= 50:
                    explanation += f"Orta hazırlık skoru ({readiness_score}) ile güvenlik iyileştirmeleri için takip edilebilir."
                else:
                    explanation += f"Düşük hazırlık skoru ({readiness_score}) ile uzun vadeli iyileştirme potansiyeli var."
            else:
                explanation += "Mevcut M365 müşterisi, güvenlik ve upsell fırsatları için değerlendirilebilir."
            return explanation
        else:
            return f"Bu lead Existing segmentinde ancak provider M365 değil ({provider}). Bu durum veri tutarsızlığı olabilir."
    
    elif segment == "Migration":
        explanation = f"Bu lead **Migration** segmentinde çünkü: "
        
        # Provider-based explanation
        if provider in ["Google", "Yandex", "Zoho", "Hosting"]:
            explanation += f"{provider} kullanıyor ve "
        elif provider == "Local":
            if local_provider:
                explanation += f"{local_provider} gibi yerel bir hosting sağlayıcısı kullanıyor ve "
            else:
                explanation += "Self-hosted mail sunucusu kullanıyor ve "
        else:
            explanation += f"{provider} kullanıyor ve "
        
        # Score-based explanation
        if readiness_score is not None:
            if readiness_score >= 80:
                explanation += f"yüksek hazırlık skoru ({readiness_score}) var. "
                explanation += "SPF, DKIM ve DMARC gibi güvenlik sinyalleri güçlü, migration için hazır."
            elif readiness_score >= 70:
                explanation += f"iyi hazırlık skoru ({readiness_score}) var. "
                explanation += "Güvenlik sinyalleri mevcut, migration için uygun."
            elif readiness_score >= 60:
                explanation += f"yeterli hazırlık skoru ({readiness_score}) var. "
                explanation += "Migration potansiyeli mevcut, takip edilmeli."
            else:
                explanation += f"düşük hazırlık skoru ({readiness_score}) var. "
                explanation += "Ancak Migration segmenti için minimum skor 60 gerekiyor, bu durum veri tutarsızlığı olabilir."
        else:
            explanation += "hazırlık skoru mevcut değil. "
            explanation += "Migration potansiyeli var ancak detaylı analiz gerekli."
        
        # Security signals context
        security_signals = []
        if spf:
            security_signals.append("SPF")
        if dkim:
            security_signals.append("DKIM")
        if dmarc_policy and dmarc_policy != "none":
            security_signals.append(f"DMARC ({dmarc_policy})")
        
        if security_signals:
            explanation += f" Güvenlik sinyalleri: {', '.join(security_signals)}."
        
        return explanation
    
    elif segment == "Cold":
        explanation = f"Bu lead **Cold** segmentinde çünkü: "
        
        # Check if it's Local-specific Cold or general Cold
        if provider == "Local" and readiness_score is not None and 5 <= readiness_score <= 59:
            explanation += f"Self-hosted mail sunucusu kullanıyor (Local provider) ve "
            if local_provider:
                explanation += f"{local_provider} gibi yerel bir hosting sağlayıcısı var. "
            explanation += f"Hazırlık skoru ({readiness_score}) düşük-orta seviyede. "
            explanation += "M365'e migration potansiyeli var ancak düşük öncelikli. "
            explanation += "Uzun vadeli takip ve bilgilendirme stratejisi uygun."
        else:
            # General Cold segment
            if readiness_score is not None:
                if 40 <= readiness_score <= 59:
                    explanation += f"hazırlık skoru ({readiness_score}) orta seviyede ancak migration için yeterli değil. "
                else:
                    explanation += f"hazırlık skoru ({readiness_score}) düşük. "
            else:
                explanation += "hazırlık skoru mevcut değil. "
            
            explanation += "Zayıf sinyaller mevcut, daha fazla veri ve analiz gerekli. "
            explanation += "Provider: " + (provider or "Bilinmiyor") + ". "
            explanation += "1-2 ay sonra tekrar değerlendirme yapılabilir."
        
        return explanation
    
    elif segment == "Skip":
        explanation = f"Bu lead **Skip** segmentinde çünkü: "
        
        if readiness_score is not None:
            if readiness_score <= 39:
                explanation += f"hazırlık skoru ({readiness_score}) çok düşük. "
            else:
                explanation += f"hazırlık skoru ({readiness_score}) yetersiz. "
        else:
            explanation += "hazırlık skoru mevcut değil. "
        
        if provider == "Local" and readiness_score is not None and readiness_score <= 4:
            explanation += "Local provider kullanıyor ve skor çok düşük (0-4). "
            explanation += "Yetersiz veri ve zayıf sinyaller nedeniyle şu an için takip edilmemeli."
        else:
            explanation += "Yetersiz veri ve zayıf sinyaller nedeniyle şu an için analiz dışı. "
            explanation += "3-6 ay sonra tekrar kontrol edilebilir."
        
        return explanation
    
    else:
        return f"Bu lead {segment} segmentinde. Segment açıklaması mevcut değil."


def explain_provider(
    domain: str,
    provider: Optional[str],
    mx_root: Optional[str] = None,
    spf: Optional[bool] = None,
    dmarc_policy: Optional[str] = None,
    local_provider: Optional[str] = None,
    infrastructure_summary: Optional[str] = None,
) -> str:
    """
    Generate AI explanation for why a lead has a specific provider.
    
    Args:
        domain: Domain name
        provider: Provider name (M365, Google, Local, etc.)
        mx_root: Root domain of MX record (e.g., "outlook.com", "aspmx.l.google.com")
        spf: SPF record exists
        dmarc_policy: DMARC policy (none, quarantine, reject)
        local_provider: Local provider name (e.g., TürkHost, Natro)
        infrastructure_summary: IP enrichment summary (e.g., "Hosted on DataCenter, ISP: Hetzner, Country: DE")
    
    Returns:
        Human-readable explanation of why the lead has this provider
    """
    if not provider:
        return "Provider bilgisi mevcut değil."
    
    # M365 provider
    if provider == "M365":
        explanation = f"Bu lead **Microsoft 365 (M365)** kullanıyor çünkü: "
        
        if mx_root:
            if "outlook.com" in mx_root.lower() or "protection.outlook.com" in mx_root.lower():
                explanation += f"MX kayıtları {mx_root} adresine işaret ediyor, bu Microsoft'un e-posta altyapısını gösteriyor. "
            else:
                explanation += f"MX kayıtları {mx_root} adresine işaret ediyor. "
        else:
            explanation += "MX kayıtları Microsoft altyapısına işaret ediyor. "
        
        if spf:
            explanation += "SPF kaydı Microsoft'u include ediyor, bu da M365 kullanımını doğruluyor. "
        
        if infrastructure_summary:
            explanation += f"Altyapı analizi: {infrastructure_summary}. "
        
        explanation += "Mevcut müşteri, güvenlik ve upsell fırsatları için değerlendirilebilir."
        return explanation
    
    # Google provider
    elif provider == "Google":
        explanation = f"Bu lead **Google Workspace** kullanıyor çünkü: "
        
        if mx_root:
            if "google.com" in mx_root.lower() or "googlemail.com" in mx_root.lower():
                explanation += f"MX kayıtları {mx_root} adresine işaret ediyor, bu Google'un e-posta altyapısını gösteriyor. "
            else:
                explanation += f"MX kayıtları {mx_root} adresine işaret ediyor. "
        else:
            explanation += "MX kayıtları Google altyapısına işaret ediyor. "
        
        explanation += "Tipik bulut e-posta servisi, Microsoft 365'e geçiş için migration fırsatı var."
        return explanation
    
    # Yandex provider
    elif provider == "Yandex":
        explanation = f"Bu lead **Yandex Mail** kullanıyor çünkü: "
        
        if mx_root:
            explanation += f"MX kayıtları {mx_root} adresine işaret ediyor, bu Yandex'in e-posta altyapısını gösteriyor. "
        else:
            explanation += "MX kayıtları Yandex altyapısına işaret ediyor. "
        
        explanation += "Bulut e-posta servisi, Microsoft 365'e geçiş için migration fırsatı var."
        return explanation
    
    # Zoho provider
    elif provider == "Zoho":
        explanation = f"Bu lead **Zoho Mail** kullanıyor çünkü: "
        
        if mx_root:
            explanation += f"MX kayıtları {mx_root} adresine işaret ediyor, bu Zoho'nun e-posta altyapısını gösteriyor. "
        else:
            explanation += "MX kayıtları Zoho altyapısına işaret ediyor. "
        
        explanation += "Bulut e-posta servisi, Microsoft 365'e geçiş için migration fırsatı var."
        return explanation
    
    # Hosting provider
    elif provider == "Hosting":
        explanation = f"Bu lead **Hosting sağlayıcısı** kullanıyor çünkü: "
        
        if mx_root:
            explanation += f"MX kayıtları {mx_root} adresine işaret ediyor, bu genelde paylaşımlı hosting altyapısını gösteriyor. "
        else:
            explanation += "MX kayıtları hosting sağlayıcısı altyapısına işaret ediyor. "
        
        explanation += "Genelde paylaşımlı mail altyapısı, teslimat ve güvenlik riski daha yüksek. "
        explanation += "Microsoft 365'e geçiş ile güvenlik ve deliverability iyileştirilebilir."
        return explanation
    
    # Local provider
    elif provider == "Local":
        explanation = f"Bu lead **Self-hosted mail sunucusu** kullanıyor çünkü: "
        
        if local_provider:
            explanation += f"MX kayıtları {local_provider} gibi yerel bir hosting sağlayıcısına ({mx_root or 'bilinmeyen'}) işaret ediyor. "
        elif mx_root:
            explanation += f"MX kayıtları {mx_root} adresine işaret ediyor, bu self-hosted veya yerel bir mail sunucusunu gösteriyor. "
        else:
            explanation += "MX kayıtları self-hosted veya yerel bir mail sunucusuna işaret ediyor. "
        
        explanation += "Genelde paylaşımlı mail altyapısı, teslimat ve güvenlik riski daha yüksek. "
        explanation += "Microsoft 365'e geçiş ile güvenlik, deliverability ve ölçeklenebilirlik iyileştirilebilir."
        return explanation
    
    # Unknown provider
    elif provider == "Unknown":
        explanation = f"Bu lead için **provider bilgisi belirsiz** çünkü: "
        
        if not mx_root:
            explanation += "MX kaydı bulunamadı veya yorumlanamıyor. "
        else:
            explanation += f"MX kaydı ({mx_root}) bilinen bir provider'a uymuyor. "
        
        explanation += "Bu durumda e-posta altyapısı net değil; bu hem risk hem fırsat. "
        explanation += "Detaylı analiz ve migration potansiyeli değerlendirilebilir."
        return explanation
    
    # Other providers (Amazon, SendGrid, Mailgun, etc.)
    else:
        explanation = f"Bu lead **{provider}** kullanıyor çünkü: "
        
        if mx_root:
            explanation += f"MX kayıtları {mx_root} adresine işaret ediyor, bu {provider} altyapısını gösteriyor. "
        else:
            explanation += f"MX kayıtları {provider} altyapısına işaret ediyor. "
        
        explanation += "Microsoft 365'e geçiş için migration potansiyeli değerlendirilebilir."
        return explanation


def explain_security_signals(
    spf: Optional[bool],
    dkim: Optional[bool],
    dmarc_policy: Optional[str],
    dmarc_coverage: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Generate AI explanation for security signals (SPF/DKIM/DMARC) with risk assessment.
    
    Args:
        spf: SPF record exists
        dkim: DKIM record exists
        dmarc_policy: DMARC policy (none, quarantine, reject)
        dmarc_coverage: DMARC coverage percentage (0-100)
    
    Returns:
        Dictionary with risk_level, summary, details, sales_angle, recommended_action
        Returns None if all signals are unknown/None (no noise for Cold/Unknown domains)
    """
    # If all signals are unknown/None, return None (no noise)
    if spf is None and dkim is None and dmarc_policy is None:
        return None
    
    details = []
    risk_factors = []
    
    # Check SPF
    if spf is False:
        details.append("SPF kaydı eksik")
        risk_factors.append("spf_missing")
    elif spf is True:
        details.append("SPF kaydı mevcut")
    
    # Check DKIM
    if dkim is False:
        details.append("DKIM kaydı eksik")
        risk_factors.append("dkim_missing")
    elif dkim is True:
        details.append("DKIM kaydı mevcut")
    
    # Check DMARC
    if dmarc_policy is None or dmarc_policy == "none":
        details.append("DMARC politikası yok")
        risk_factors.append("dmarc_missing")
    elif dmarc_policy in ["quarantine", "reject"]:
        details.append(f"DMARC politikası: {dmarc_policy}")
        if dmarc_coverage is not None and dmarc_coverage < 100:
            details.append(f"DMARC kapsamı: %{dmarc_coverage} (tam kapsam değil)")
            risk_factors.append("dmarc_partial")
        elif dmarc_coverage is not None and dmarc_coverage == 100:
            details.append("DMARC kapsamı: %100 (tam koruma)")
    
    # Determine risk level
    risk_level = "low"
    if len(risk_factors) >= 3:  # SPF + DKIM + DMARC all missing
        risk_level = "high"
    elif len(risk_factors) >= 2:  # At least 2 missing
        risk_level = "high"
    elif "dmarc_missing" in risk_factors:  # DMARC is critical
        risk_level = "high"
    elif "dmarc_partial" in risk_factors or len(risk_factors) == 1:
        risk_level = "medium"
    
    # Generate summary
    if risk_level == "high":
        if "dmarc_missing" in risk_factors:
            # Check SPF and DKIM status for accurate messaging
            if spf is True and dkim is True:
                summary = "DMARC yok. SPF ve DKIM mevcut, ancak DMARC eksik olduğu için spoofing riski hâlâ yüksek."
            elif spf is True and dkim is False:
                # v1.1: More specific - SPF exists but DKIM missing
                summary = "DMARC yok. SPF mevcut ancak DKIM eksik, yapı eksik ve spoofing riski yüksek."
            elif spf is False and dkim is True:
                # v1.1: More specific - DKIM exists but SPF missing
                summary = "DMARC yok. DKIM mevcut ancak SPF eksik, yapı eksik ve spoofing riski yüksek."
            elif spf is True or dkim is True:
                # Fallback for edge cases (should not happen with above conditions)
                summary = "DMARC yok. SPF veya DKIM'den sadece biri var, yapı eksik ve spoofing riski yüksek."
            else:
                summary = "DMARC, SPF ve DKIM yok. Spoofing ve phishing riski kritik seviyede."
        elif len(risk_factors) >= 2:
            summary = "SPF ve DKIM eksik, DMARC yok. Email güvenliği kritik seviyede zayıf."
        else:
            summary = "Email güvenlik sinyalleri eksik. Phishing ve spoofing saldırılarına açık."
    elif risk_level == "medium":
        if "dmarc_partial" in risk_factors:
            summary = f"DMARC mevcut ancak kapsamı sadece %{dmarc_coverage}. Tam koruma için iyileştirme gerekli."
        else:
            summary = "Email güvenlik sinyalleri kısmen mevcut. DMARC eklenmesi önerilir."
    else:  # low
        summary = "SPF, DKIM ve DMARC mevcut. Email güvenliği iyi seviyede."
    
    # Generate sales angle
    if risk_level == "high":
        sales_angle = "Güvenlik açığı üzerinden konuşma aç: phishing, sahte fatura, iç yazışma taklidi. "
        sales_angle += "Bu durum hem müşteri güvenini hem de marka itibarını riske atıyor."
    elif risk_level == "medium":
        sales_angle = "Güvenlik iyileştirme fırsatı: mevcut altyapıyı güçlendirerek tam koruma sağlanabilir. "
        sales_angle += "DMARC tam kapsamı ile email deliverability de artar."
    else:  # low
        sales_angle = "Güvenlik altyapısı iyi durumda. Defender ve ek güvenlik çözümleri ile daha da güçlendirilebilir."
    
    # Generate recommended action
    if risk_level == "high":
        recommended_action = "Microsoft 365 + Defender ile DMARC/SPF/DKIM tam koruma öner. "
        recommended_action += "Acil aksiyon: phishing ve spoofing saldırılarına karşı koruma kritik."
    elif risk_level == "medium":
        recommended_action = "Microsoft 365'e geçiş veya mevcut altyapıda DMARC tam kapsamı sağlanmalı. "
        recommended_action += "Güvenlik iyileştirmesi ile email deliverability %40'a kadar artabilir."
    else:  # low
        recommended_action = "Mevcut güvenlik altyapısını koruyarak Microsoft Defender for Office 365 ile ek koruma katmanı eklenebilir."
    
    return {
        "risk_level": risk_level,
        "summary": summary,
        "details": details,
        "sales_angle": sales_angle,
        "recommended_action": recommended_action,
    }


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
    security_reasoning: Optional[Dict[str, Any]] = None,
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
        ip_context: Optional IP enrichment context
        security_reasoning: Optional security reasoning dict (from explain_security_signals)

    Returns:
        List of call script bullets
    """
    bullets = []

    # IP context integration (optional, for intelligent text generation)
    ip_country = ip_context.get("country") if ip_context else None
    ip_is_proxy = ip_context.get("is_proxy") if ip_context else None
    ip_city = ip_context.get("city") if ip_context else None

    # Cold segment - special soft, discovery-focused script (v1.1)
    if segment == "Cold":
        # 1. Soft opening + context
        bullets.append(
            f"Merhaba, ben Gibibyte'dan arıyorum. {domain} için genel bir email altyapısı taraması yaptık."
        )
        
        # 2. Value proposition (soft, discovery-focused)
        if security_reasoning and security_reasoning.get("risk_level") == "high":
            # High risk security - more direct but still soft
            bullets.append(
                "Basit bir dış göz olarak, spoofing ve phishing saldırılarına açık olabilecek bazı noktalar gördük."
            )
        else:
            # General improvement potential
            bullets.append(
                "Özellikle spam, teslimat ve güvenlik tarafında iyileştirme potansiyeli olabilecek yerler gördük."
            )
        
        # 3. Discovery-focused CTA
        bullets.append(
            "İsterseniz 10-15 dakikalık kısa bir görüşmede mevcut durumu üzerinden geçip, olası risk ve fırsatları birlikte değerlendirebiliriz."
        )
        
        return bullets

    # Migration segment - existing logic (preserved)
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
        
        # Security signals (if not already covered by security_reasoning)
        if not security_reasoning:
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

        # Value proposition based on tenant size
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
        
        # Call to action
        if readiness_score and readiness_score >= 70:
            bullets.append(
                "15 dakikalık kısa bir görüşme yapabilir miyiz? Size özel bir teklif hazırlayabilirim."
            )
        else:
            bullets.append(
                "Size özel bir teklif hazırlamak için kısa bir görüşme yapabilir miyiz?"
            )
        
        return bullets

    # Existing segment - existing logic (preserved)
    if segment == "Existing":
        bullets.append(
            f"Merhaba, {domain} için mevcut Microsoft 365 altyapınızı inceledik ve güvenlik iyileştirmeleri için önerilerimiz var."
        )
        
        # Security signals (if not already covered by security_reasoning)
        if not security_reasoning:
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
        
        bullets.append(
            "Microsoft Defender for Office 365 ve ek güvenlik çözümlerimiz ile mevcut altyapınızı güçlendirebiliriz."
        )
        
        bullets.append(
            "Mevcut altyapınızı değerlendirmek için kısa bir görüşme yapabilir miyiz?"
        )
        
        return bullets

    # Default/Other segments (Skip, etc.) - generic script
    bullets.append(
        f"Merhaba, {domain} için email güvenliği ve altyapı analizi yaptık ve sizinle paylaşmak istediğimiz önemli bulgular var."
    )
    
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


def explain_opportunity_potential(
    segment: Optional[str],
    readiness_score: Optional[int],
    priority_score: Optional[int],
    tenant_size: Optional[str],
    contact_quality_score: Optional[int] = None,
    tuning_factor: float = 1.0,
) -> Dict[str, Any]:
    """
    Explain opportunity potential score with breakdown of contributing factors.
    
    Args:
        segment: Lead segment (Migration, Existing, Cold, Skip)
        readiness_score: Readiness score (0-100)
        priority_score: Priority score (1-7, 1 is highest)
        tenant_size: Tenant size (small, medium, large)
        contact_quality_score: Contact quality score (0-100)
        tuning_factor: Tuning factor (default: 1.0)
    
    Returns:
        Dictionary with total score, factors breakdown, and summary
    """
    factors = []
    base_score = 0
    
    # Segment contribution (40 points max)
    segment_score = 0
    segment_weight = 0.4
    if segment == "Migration":
        segment_score = 40
        segment_comment = "Migration segment: yüksek potansiyel, hemen aksiyon alınabilir."
    elif segment == "Existing":
        segment_score = 30
        segment_comment = "Existing segment: mevcut müşteri, upsell fırsatı."
    elif segment == "Cold":
        segment_score = 15
        segment_comment = "Cold lead, bu yüzden başlangıç puanı düşük tutuldu."
    else:  # Skip
        segment_score = 5
        segment_comment = "Skip segmenti: düşük öncelik."
    
    base_score += segment_score
    factors.append({
        "name": "segment",
        "weight": segment_weight,
        "raw": segment or "Unknown",
        "score": segment_score,
        "comment": segment_comment,
    })
    
    # Readiness score contribution (30 points max)
    readiness_weight = 0.3
    if readiness_score:
        readiness_contribution = int(readiness_score * 0.3)
        if readiness_score >= 80:
            readiness_comment = f"Hazırlık skoru yüksek ({readiness_score}). Hemen aksiyon alınabilir."
        elif readiness_score >= 50:
            readiness_comment = f"Hazırlık skoru orta seviyede ({readiness_score}). Orta vadeli takip için uygun."
        else:
            readiness_comment = f"Hazırlık skoru düşük ({readiness_score}). Uzun vadeli takip gerekebilir."
    else:
        readiness_contribution = 10
        readiness_comment = "Hazırlık skoru mevcut değil, varsayılan değer kullanıldı."
    
    base_score += readiness_contribution
    factors.append({
        "name": "readiness_score",
        "weight": readiness_weight,
        "raw": readiness_score,
        "score": readiness_contribution,
        "comment": readiness_comment,
    })
    
    # Priority score contribution (20 points max) - inverse
    priority_weight = 0.2
    if priority_score:
        if priority_score == 1:
            priority_contribution = 20
            priority_comment = "Priority 1: en yüksek öncelikli fırsat, acil aksiyon gerekli."
        elif priority_score == 2:
            priority_contribution = 18
            priority_comment = "Priority 2: yüksek öncelikli fırsat."
        elif priority_score == 3:
            priority_contribution = 15
            priority_comment = "Priority 3: orta-yüksek öncelikli fırsat."
        elif priority_score == 4:
            priority_contribution = 12
            priority_comment = "Priority 4: orta öncelikli fırsat."
        elif priority_score == 5:
            priority_contribution = 8
            priority_comment = "Priority 5: orta öncelikli fırsat."
        elif priority_score == 6:
            priority_contribution = 5
            priority_comment = "Priority 6: düşük öncelikli fırsat."
        else:  # 7
            priority_contribution = 2
            priority_comment = "Priority 7: en düşük öncelikli fırsat."
    else:
        priority_contribution = 5
        priority_comment = "Priority skoru mevcut değil, varsayılan değer kullanıldı."
    
    base_score += priority_contribution
    factors.append({
        "name": "priority_score",
        "weight": priority_weight,
        "raw": priority_score,
        "score": priority_contribution,
        "comment": priority_comment,
    })
    
    # Tenant size contribution (10 points max)
    tenant_weight = 0.1
    if tenant_size == "large":
        tenant_contribution = 10
        tenant_comment = "Büyük ölçekli tenant → yüksek fırsat boyutu, Enterprise çözüm potansiyeli."
    elif tenant_size == "medium":
        tenant_contribution = 7
        tenant_comment = "Orta ölçekli tenant → dengeli fırsat boyutu."
    elif tenant_size == "small":
        tenant_contribution = 5
        tenant_comment = "Küçük ölçekli tenant → fırsat boyutu sınırlı ama hızlı karar alınabilir."
    else:
        tenant_contribution = 3
        tenant_comment = "Tenant boyutu bilinmiyor, varsayılan değer kullanıldı."
    
    base_score += tenant_contribution
    factors.append({
        "name": "tenant_size",
        "weight": tenant_weight,
        "raw": tenant_size or "Unknown",
        "score": tenant_contribution,
        "comment": tenant_comment,
    })
    
    # Contact quality bonus (5 points max)
    contact_contribution = 0
    if contact_quality_score:
        contact_contribution = int(contact_quality_score * 0.05)
        base_score += contact_contribution
        factors.append({
            "name": "contact_quality",
            "weight": 0.05,
            "raw": contact_quality_score,
            "score": contact_contribution,
            "comment": f"İletişim kalitesi skoru ({contact_quality_score}) bonus puan ekledi.",
        })
    
    # Apply tuning factor
    total = int(base_score * tuning_factor)
    total = min(total, 100)  # Cap at 100
    
    # Generate summary
    if segment == "Migration":
        if readiness_score and readiness_score >= 80:
            summary = f"Migration segment, yüksek hazırlık skoru ({readiness_score}) ve yüksek öncelik nedeniyle fırsat puanı {total}."
        else:
            summary = f"Migration segment, orta hazırlık skoru ve öncelik nedeniyle fırsat puanı {total}."
    elif segment == "Existing":
        summary = f"Existing segment, mevcut müşteri upsell fırsatı nedeniyle fırsat puanı {total}."
    elif segment == "Cold":
        summary = f"Cold segment, orta hazırlık skoru ve orta öncelik nedeniyle fırsat puanı {total} civarında."
    else:
        summary = f"Skip segmenti, düşük öncelik nedeniyle fırsat puanı {total}."
    
    return {
        "total": total,
        "factors": factors,
        "tuning_factor": tuning_factor,
        "summary": summary,
    }


def generate_next_step_cta(
    segment: Optional[str],
    opportunity_potential: Optional[int],
    urgency: Optional[str],
    tenant_size: Optional[str] = None,
) -> Dict[str, str]:
    """
    Generate next-step CTA (Call To Action) for sales rep.
    
    Args:
        segment: Lead segment (Migration, Existing, Cold, Skip)
        opportunity_potential: Opportunity potential score (0-100)
        urgency: Urgency level (low, medium, high)
        tenant_size: Tenant size (small, medium, large)
    
    Returns:
        Dictionary with action, timeline, priority, message, and internal_note
    """
    # Default values
    action = "wait"
    timeline = "1_ay"
    priority = "low"
    message = "Bu lead için şu an için özel bir aksiyon gerekmiyor. Yeni sinyaller geldiğinde tekrar değerlendirilebilir."
    internal_note = "Düşük öncelikli lead. Sistem yeni sinyal üretirse tekrar bakılabilir."
    
    # Skip segment or very low opportunity
    if segment == "Skip" or (opportunity_potential is not None and opportunity_potential < 20):
        return {
            "action": "wait",
            "timeline": "1_ay",
            "priority": "low",
            "message": "Bu lead için şu an için özel bir aksiyon gerekmiyor. Yeni sinyaller geldiğinde tekrar değerlendirilebilir.",
            "internal_note": "Skip segmenti veya çok düşük fırsat skoru. Sistem yeni sinyal üretirse tekrar bakılabilir.",
        }
    
    # High opportunity (>= 80) + Migration/Existing + high/medium urgency
    if (
        opportunity_potential is not None
        and opportunity_potential >= 80
        and segment in ["Migration", "Existing"]
        and urgency in ["high", "medium"]
    ):
        action = "call"
        timeline = "24_saat"
        priority = "high"
        
        if segment == "Migration":
            message = "Mevcut altyapınızdan Microsoft 365'e geçişle ilgili hızlıca bir planlama yapabiliriz. 15 dakikalık bir görüşme ayarlayalım mı?"
            internal_note = "High potential migration lead. İlk 24 saat içinde aranmalı. Hemen aksiyon alınabilir."
        else:  # Existing
            message = "Mevcut Microsoft 365 altyapınızı değerlendirip güvenlik iyileştirmeleri için önerilerimizi paylaşabiliriz. Kısa bir görüşme ayarlayalım mı?"
            internal_note = "High potential existing customer upsell. İlk 24 saat içinde aranmalı."
    
    # Medium opportunity (50-79)
    elif opportunity_potential is not None and 50 <= opportunity_potential < 80:
        if segment == "Cold":
            action = "call"
            timeline = "3_gün"
            priority = "medium"
            message = "Email altyapınızla ilgili kısa bir değerlendirme yaptık. İsterseniz 10-15 dakikalık bir görüşmede mevcut durumu ve olası iyileştirmeleri birlikte değerlendirebiliriz."
            internal_note = "Orta seviye fırsat, Cold lead. 3 gün içinde aranmalı."
        elif segment == "Existing":
            action = "call"
            timeline = "3_gün"
            priority = "medium"
            message = "Mevcut Microsoft 365 altyapınızı değerlendirip güvenlik iyileştirmeleri için önerilerimizi paylaşabiliriz. Kısa bir görüşme ayarlayalım mı?"
            internal_note = "Orta seviye fırsat, Existing customer. 3 gün içinde aranmalı."
        else:  # Migration
            action = "call"
            timeline = "3_gün"
            priority = "medium"
            message = "Microsoft 365'e geçiş potansiyeli görüyoruz. Size özel bir teklif hazırlamak için kısa bir görüşme yapabilir miyiz?"
            internal_note = "Orta seviye fırsat, Migration lead. 3 gün içinde aranmalı."
    
    # Low opportunity (< 50) + Cold
    elif opportunity_potential is not None and opportunity_potential < 50:
        if segment == "Cold":
            action = "email"
            timeline = "1_hafta"
            priority = "low"
            message = "İsterseniz mevcut email altyapınızla ilgili kısa bir değerlendirme dokümanı paylaşabilirim, size uygun bir zamanda üzerinden geçeriz."
            internal_note = "Cold lead, düşük fırsat. Önce email + nurturing, sonra durum değişirse arama."
        else:
            # Other segments with low opportunity
            action = "email"
            timeline = "1_hafta"
            priority = "low"
            message = "Email altyapınızla ilgili değerlendirme sonuçlarını paylaşmak için kısa bir görüşme yapabilir miyiz?"
            internal_note = "Düşük fırsat skoru. Email ile başlayıp sonra arama yapılabilir."
    
    # Fallback: Use urgency and segment if opportunity_potential is None
    elif urgency == "high":
        action = "call"
        timeline = "24_saat"
        priority = "high"
        message = "Yüksek öncelikli bir fırsat görüyoruz. Hemen bir görüşme ayarlayalım mı?"
        internal_note = "High urgency lead. İlk 24 saat içinde aranmalı."
    elif urgency == "medium":
        action = "call"
        timeline = "3_gün"
        priority = "medium"
        message = "Size özel bir değerlendirme yaptık. Kısa bir görüşme yapabilir miyiz?"
        internal_note = "Medium urgency lead. 3 gün içinde aranmalı."
    elif segment == "Migration":
        action = "call"
        timeline = "1_hafta"
        priority = "medium"
        message = "Microsoft 365'e geçiş potansiyeli görüyoruz. Size özel bir teklif hazırlamak için kısa bir görüşme yapabilir miyiz?"
        internal_note = "Migration lead. 1 hafta içinde aranmalı."
    elif segment == "Existing":
        action = "email"
        timeline = "1_hafta"
        priority = "medium"
        message = "Mevcut Microsoft 365 altyapınızı değerlendirip güvenlik iyileştirmeleri için önerilerimizi paylaşabiliriz."
        internal_note = "Existing customer. Email ile başlayıp sonra arama yapılabilir."
    
    return {
        "action": action,
        "timeline": timeline,
        "priority": priority,
        "message": message,
        "internal_note": internal_note,
    }


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
    mx_root: Optional[str] = None,
    infrastructure_summary: Optional[str] = None,
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
        "segment_explanation": explain_segment(
            segment, provider, readiness_score, local_provider, spf, dkim, dmarc_policy
        ),
        "provider_reasoning": explain_provider(
            domain, provider, mx_root, spf, dmarc_policy, local_provider, infrastructure_summary
        ),
        "security_reasoning": explain_security_signals(
            spf, dkim, dmarc_policy, dmarc_coverage
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
            security_reasoning=explain_security_signals(spf, dkim, dmarc_policy, dmarc_coverage),
        ),
        "discovery_questions": generate_discovery_questions(
            segment, provider, tenant_size
        ),
        "offer_tier": recommend_offer_tier(tenant_size, segment, readiness_score),
        "opportunity_potential": calculate_opportunity_potential(
            segment, readiness_score, priority_score, tenant_size, contact_quality_score, tuning_factor
        ),
        "opportunity_rationale": explain_opportunity_potential(
            segment, readiness_score, priority_score, tenant_size, contact_quality_score, tuning_factor
        ),
        "urgency": calculate_urgency(segment, priority_score, readiness_score, expires_at),
        "next_step": generate_next_step_cta(
            segment,
            calculate_opportunity_potential(
                segment, readiness_score, priority_score, tenant_size, contact_quality_score, tuning_factor
            ),
            calculate_urgency(segment, priority_score, readiness_score, expires_at),
            tenant_size,
        ),
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

