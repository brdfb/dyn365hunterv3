// UI Leads - Table and filter rendering

import { log, warn, error as logError } from './logger.js';
import { escapeHtml } from './utils.js';

/**
 * Render leads table
 */
export function renderLeadsTable(leads) {
    const tbody = document.getElementById('leads-table-body');
    const emptyState = document.getElementById('empty-state');
    
    if (!leads || leads.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    
    tbody.innerHTML = leads.map(lead => {
        const segmentClass = getSegmentClass(lead.segment);
        const scoreClass = getScoreClass(lead.readiness_score);
        // Phase 3: Use P-model priority_category and priority_label
        const priorityBadge = getPriorityBadge(lead.priority_category || lead.priority_score);
        const priorityTooltip = getPriorityTooltip(lead.priority_category, lead.priority_label, lead.priority_score, lead.segment, lead.readiness_score);
        
        return `
            <tr class="leads-table__row">
                <td class="leads-table__cell leads-table__cell--priority" ${priorityTooltip ? `title="${escapeHtml(priorityTooltip)}"` : ''}>${priorityBadge}</td>
                <td class="leads-table__cell leads-table__cell--domain ${lead.domain && lead.domain !== '-' ? 'domain-clickable' : ''}" 
                    ${lead.domain && lead.domain !== '-' ? `data-domain="${escapeHtml(lead.domain)}"` : ''}>
                    ${escapeHtml(lead.domain || '-')}
                </td>
                <td class="leads-table__cell">${escapeHtml(lead.canonical_name || '-')}</td>
                <td class="leads-table__cell leads-table__cell--provider">
                    ${lead.provider && lead.provider !== '-' 
                        ? `<span class="provider-badge ${getProviderBadgeClass(lead.provider)}">${escapeHtml(lead.provider)}</span>`
                        : '-'
                    }
                </td>
                <td class="leads-table__cell leads-table__cell--tenant-size" title="${lead.tenant_size ? getTenantSizeTooltip(lead.tenant_size, lead.provider, lead.mx_root) : lead.provider === 'M365' || lead.provider === 'Google' ? 'Tenant Size: M365/Google provider\'ları için MX pattern\'ine göre tahmin edilir (small/medium/large)' : 'Tenant Size: Sadece M365 ve Google provider\'ları için hesaplanır'}">
                    ${lead.tenant_size ? `<span class="tenant-size-badge tenant-size-badge--${lead.tenant_size}">${escapeHtml(lead.tenant_size)}</span>` : '-'}
                </td>
                <td class="leads-table__cell leads-table__cell--local-provider" title="${lead.local_provider ? `Local Provider: ${lead.local_provider}` : lead.provider === 'Local' && lead.mx_root ? `MX Root: ${lead.mx_root} (Bilinen provider tespit edilemedi)` : lead.provider === 'Local' ? 'Local Provider: Bilinen Türk hosting provider\'ları tespit edilir (TürkHost, Natro, vb.). Bu domain için provider tespit edilemedi.' : 'Local Provider: Sadece provider "Local" olduğunda doldurulur'}">
                    ${lead.local_provider ? escapeHtml(lead.local_provider) : lead.provider === 'Local' && lead.mx_root ? `<span style="color: #666; font-size: 0.9em;" title="MX Root: ${escapeHtml(lead.mx_root)}">${escapeHtml(lead.mx_root)}</span>` : lead.provider === 'Local' ? '<span style="color: #999; font-style: italic;">Bilinmeyen</span>' : '-'}
                </td>
                <td class="leads-table__cell leads-table__cell--referral">
                    ${getReferralBadge(lead.referral_type)}
                </td>
                <td class="leads-table__cell leads-table__cell--segment">
                    ${lead.segment ? `<span class="segment-badge segment-badge--${segmentClass}" title="${getSegmentTooltip(lead.segment, lead.provider, lead.readiness_score)}">${escapeHtml(lead.segment)}</span>` : '-'}
                </td>
                <td class="leads-table__cell leads-table__cell--score ${scoreClass} ${lead.readiness_score !== null && lead.readiness_score !== undefined ? 'score-clickable' : ''}" 
                    ${lead.readiness_score !== null && lead.readiness_score !== undefined ? `data-domain="${escapeHtml(lead.domain)}"` : ''}>
                    ${lead.readiness_score !== null && lead.readiness_score !== undefined ? lead.readiness_score : '-'}
                </td>
                <td class="leads-table__cell leads-table__cell--actions">
                    ${lead.domain && lead.domain !== '-' 
                        ? `<button type="button" class="sales-button" data-domain="${escapeHtml(lead.domain)}" title="Sales Summary">📞 Sales</button>`
                        : '-'
                    }
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Render dashboard KPIs (G19 - New endpoint)
 */
export function renderKPIs(kpis) {
    if (!kpis) return;
    
    const totalEl = document.getElementById('kpi-total');
    const migrationEl = document.getElementById('kpi-migration');
    const highPriorityEl = document.getElementById('kpi-high-priority');
    const maxScoreEl = document.getElementById('kpi-max-score');
    
    if (totalEl) totalEl.textContent = kpis.total_leads || 0;
    if (migrationEl) migrationEl.textContent = kpis.migration_leads || 0;
    if (highPriorityEl) highPriorityEl.textContent = kpis.high_priority || 0;
    if (maxScoreEl) {
        // Max score is now in KPIs endpoint
        const maxScore = kpis.max_score;
        maxScoreEl.textContent = (maxScore !== null && maxScore !== undefined) ? maxScore : '-';
    }
}

/**
 * Render dashboard stats (legacy - kept for backward compatibility)
 */
export function renderStats(dashboard) {
    if (!dashboard) return;
    
    document.getElementById('kpi-total').textContent = dashboard.total_leads || 0;
    document.getElementById('kpi-migration').textContent = dashboard.migration || 0;
    
    // Display max score from backend
    const maxScore = dashboard.max_score !== null && dashboard.max_score !== undefined 
        ? dashboard.max_score 
        : '-';
    const maxScoreEl = document.getElementById('kpi-max-score');
    if (maxScoreEl) maxScoreEl.textContent = maxScore;
    
    // High priority from legacy endpoint
    const highPriorityEl = document.getElementById('kpi-high-priority');
    if (highPriorityEl) highPriorityEl.textContent = dashboard.high_priority || 0;
}

/**
 * Get segment tooltip text (v1.1: Sales-friendly explanations)
 */
function getSegmentTooltip(segment, provider = null, score = null) {
    if (!segment) return '';
    
    // Cold segment için provider'a göre özelleştirilmiş açıklama
    if (segment === 'Cold') {
        if (provider === 'Google') {
            return 'Google Workspace kullanıyor ama skor düşük (40-69) → SPF/DKIM/DMARC sinyalleri eksik olabilir. Migration potansiyeli var ama skor 70+ olmalı';
        } else if (provider === 'Yandex') {
            return 'Yandex Mail kullanıyor ama skor düşük (40-69) → SPF/DKIM/DMARC sinyalleri eksik olabilir. Migration potansiyeli var ama skor 70+ olmalı';
        } else if (provider === 'Local') {
            return 'Local hosting kullanıyor, migration potansiyeli var (skor 40-69) → M365\'e geçiş için uygun aday';
        } else if (provider === 'Hosting') {
            return 'Hosting provider kullanıyor, migration potansiyeli var (skor 40-69) → M365\'e geçiş için uygun aday';
        } else if (provider && provider !== 'Unknown') {
            return 'Email provider tespit edildi ama skor düşük (40-69) → SPF/DKIM/DMARC sinyalleri eksik olabilir. Daha fazla sinyal gerekli';
        } else {
            return 'Email provider tespit edilemedi → yeni müşteri potansiyeli';
        }
    }
    
    const tooltips = {
        'Existing': 'M365 kullanıyor → yenileme / ek lisans fırsatı',
        'Migration': 'Cloud provider kullanıyor (Google/Yandex/Zoho/Hosting/Local) → migration fırsatı (skor 70+)',
        'Skip': 'Düşük skor / risk → düşük öncelik'
    };
    return tooltips[segment] || '';
}

/**
 * Get tenant size tooltip text
 */
function getTenantSizeTooltip(tenantSize, provider, mxRoot) {
    if (!tenantSize || !provider) return `Tenant büyüklüğü: ${tenantSize}`;
    
    let explanation = '';
    if (provider === 'M365') {
        if (tenantSize === 'large') {
            explanation = 'Enterprise pattern (mail.protection.outlook.com) → 500+ kullanıcı tahmini';
        } else if (tenantSize === 'small') {
            explanation = 'Regional/OLC pattern → 1-50 kullanıcı tahmini';
        } else {
            explanation = 'Standard pattern → 50-500 kullanıcı tahmini';
        }
    } else if (provider === 'Google') {
        if (tenantSize === 'large') {
            explanation = 'Enterprise/custom pattern → 500+ kullanıcı tahmini (standart aspmx.l.google.com değil)';
        } else {
            explanation = 'Standard Google Workspace pattern (aspmx.l.google.com) → 50-500 kullanıcı tahmini';
        }
    } else {
        explanation = 'MX pattern\'ine göre tahmin edilir';
    }
    
    return `Tenant büyüklüğü: ${tenantSize} - ${explanation}${mxRoot ? ` (MX: ${mxRoot})` : ''}`;
}

/**
 * Get segment CSS class
 */
function getSegmentClass(segment) {
    if (!segment) return '';
    const lower = segment.toLowerCase();
    if (lower === 'migration') return 'migration';
    if (lower === 'existing') return 'existing';
    if (lower === 'cold') return 'cold';
    if (lower === 'skip') return 'skip';
    return '';
}

/**
 * Get provider badge class
 */
function getProviderBadgeClass(provider) {
    if (!provider || provider === '-') return '';
    const providerLower = provider.toLowerCase();
    return `provider-badge--${providerLower}`;
}

/**
 * Get score CSS class
 */
function getScoreClass(score) {
    if (score === null || score === undefined) return '';
    if (score >= 70) return 'score-high';
    if (score >= 50) return 'score-medium';
    return 'score-low';
}

/**
 * Get priority badge (P-model: P1-P6 with colored badges)
 * Phase 3: Updated to use priority_category (P1-P6) from P-model
 * Falls back to old priority_score (1-7) for backward compatibility
 */
function getPriorityBadge(priority_category_or_score) {
    if (priority_category_or_score === null || priority_category_or_score === undefined) return '-';
    
    // Phase 3: P-model priority_category (P1-P6)
    if (typeof priority_category_or_score === 'string' && priority_category_or_score.startsWith('P')) {
        const category = priority_category_or_score.toUpperCase();
        return `<span class="priority-badge priority-badge--${category.toLowerCase()}">${category}</span>`;
    }
    
    // Backward compatibility: Old priority_score (1-7)
    const priority_score = priority_category_or_score;
    switch (priority_score) {
        case 1:
            return '🔥'; // Highest priority (Migration 80+)
        case 2:
            return '⭐'; // High priority (Migration 70-79)
        case 3:
            return '🟡'; // Medium-high priority (Migration 50-69, Existing 70+)
        case 4:
            return '🟠'; // Medium priority (Migration 0-49, Existing 50-69)
        case 5:
            return '⚪'; // Low-medium priority (Existing 30-49, Cold 40+)
        case 6:
            return '⚫'; // Low priority (Existing 0-29, Cold 20-39)
        case 7:
            return '🔴'; // Lowest priority (Cold 0-19, Skip)
        default:
            return '-'; // Unknown
    }
}

/**
 * Get referral badge (Task 2.5: Partner Center referral type)
 * Badge colors: co-sell (blue), marketplace (green), solution-provider (orange)
 */
function getReferralBadge(referral_type) {
    if (!referral_type) return '-';
    
    const type = referral_type.toLowerCase();
    const labels = {
        'co-sell': 'Co-sell',
        'marketplace': 'Marketplace',
        'solution-provider': 'SP'
    };
    
    const label = labels[type] || referral_type;
    // CSS class uses the type as-is (co-sell, marketplace, solution-provider)
    const cssType = type;  // Already in correct format for CSS class
    const badgeClass = `referral-badge referral-badge--${cssType}`;
    
    return `<span class="${badgeClass}">${escapeHtml(label)}</span>`;
}

/**
 * Get priority tooltip text
 * Phase 3: Updated to use priority_label from P-model
 * Falls back to old priority_score-based tooltip for backward compatibility
 */
function getPriorityTooltip(priority_category, priority_label, priority_score, segment, score) {
    // Phase 3: P-model priority_label (preferred)
    if (priority_category && priority_label) {
        return priority_label;
    }
    
    // Backward compatibility: Old priority_score-based tooltip
    if (priority_score === null || priority_score === undefined) return '';
    
    const segmentText = segment || 'Bilinmeyen';
    const scoreText = score !== null && score !== undefined ? score : 'N/A';
    
    switch (priority_score) {
        case 1:
            return `🔥 En yüksek öncelik - ${segmentText} segment, Skor ${scoreText}+`;
        case 2:
            return `⭐ Yüksek öncelik - ${segmentText} segment, Skor ${scoreText}`;
        case 3:
            return `🟡 Orta-yüksek öncelik - ${segmentText} segment, Skor ${scoreText}`;
        case 4:
            return `🟠 Orta öncelik - ${segmentText} segment, Skor ${scoreText}`;
        case 5:
            return `⚪ Düşük-orta öncelik - ${segmentText} segment, Skor ${scoreText}`;
        case 6:
            return `⚫ Düşük öncelik - ${segmentText} segment, Skor ${scoreText}`;
        case 7:
            return `🔴 En düşük öncelik - ${segmentText} segment, Skor ${scoreText}`;
        default:
            return '';
    }
}


/**
 * Show loading indicator
 */
/**
 * Set table loading state (Phase 1.3)
 */
export function setTableLoading(isLoading) {
    const wrapper = document.getElementById('leads-table-wrapper');
    const loading = document.getElementById('leads-table-loading');
    const table = document.getElementById('leads-table');
    
    if (wrapper && loading && table) {
        if (isLoading) {
            loading.classList.remove('hidden');
            table.classList.add('is-loading');
        } else {
            loading.classList.add('hidden');
            table.classList.remove('is-loading');
        }
    }
}

/**
 * Set filters loading state (Phase 1.3)
 */
export function setFiltersLoading(isLoading) {
    const filterControls = document.querySelectorAll('.js-filter-control');
    filterControls.forEach(el => {
        el.disabled = !!isLoading;
    });
}

/**
 * Set export buttons loading state (Phase 1.3)
 */
export function setExportLoading(isLoading) {
    const exportButtons = document.querySelectorAll('.js-export-button');
    exportButtons.forEach(btn => {
        btn.disabled = !!isLoading;
        btn.classList.toggle('is-loading', !!isLoading);
    });
}

export function showLoading() {
    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
        loadingEl.innerHTML = `
            <div class="leads-loading">
                <div class="leads-loading__spinner"></div>
                <span>Lead'ler yükleniyor...</span>
            </div>
        `;
        loadingEl.style.display = 'block';
    }
    document.getElementById('error').style.display = 'none';
}

/**
 * Hide loading indicator
 */
export function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

/**
 * Show error message
 */
/**
 * Show error message (v1.1: Sales-friendly messages)
 */
export function showError(message) {
    const errorEl = document.getElementById('error');
    if (!errorEl) return;
    
    // v1.1: Convert technical errors to sales-friendly messages
    let friendlyMessage = message;
    
    // Network errors
    if (message.includes('Failed to fetch') || message.includes('NetworkError') || message.includes('fetch')) {
        friendlyMessage = 'Sunucuya ulaşamadık. Birkaç dakika sonra tekrar dene.';
    }
    // Server errors
    else if (message.includes('500') || message.includes('Internal Server Error')) {
        friendlyMessage = 'Bir şeyler ters gitti. Lütfen daha sonra tekrar dene.';
    }
    // Timeout errors
    else if (message.includes('timeout') || message.includes('Timeout')) {
        friendlyMessage = 'İstek zaman aşımına uğradı. Lütfen tekrar dene.';
    }
    // Generic API errors
    else if (message.includes('yüklenemedi') || message.includes('hatası')) {
        // Keep Turkish error messages as-is but make them friendlier
        friendlyMessage = message.replace(/yüklenemedi/g, 'yüklenemedi').replace(/hatası/g, 'sorunu');
    }
    
    // Log technical details to console (not shown to user)
    if (message !== friendlyMessage) {
        logError('Technical error (hidden from user):', message);
    }
    
    errorEl.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.25rem;">⚠️</span>
            <div>
                <strong>Bir şeyler ters gitti</strong>
                <div style="margin-top: 0.25rem; font-size: 0.9rem;">${escapeHtml(friendlyMessage)}</div>
            </div>
        </div>
    `;
    errorEl.style.display = 'block';
    errorEl.style.position = 'sticky';
    errorEl.style.top = '0';
    errorEl.style.zIndex = '1000';
    errorEl.style.marginBottom = '1rem';
    
    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
        loadingEl.style.display = 'none';
    }
}

/**
 * Hide error message
 */
export function hideError() {
    document.getElementById('error').style.display = 'none';
}

/**
 * Get user-friendly signal label
 */
function getSignalLabel(signal) {
    const labels = {
        'spf': 'SPF',
        'dkim': 'DKIM',
        'dmarc_quarantine': 'DMARC Quarantine',
        'dmarc_reject': 'DMARC Reject',
        'dmarc_none': 'DMARC None'
    };
    return labels[signal] || signal.toUpperCase();
}

/**
 * Get user-friendly risk label
 */
function getRiskLabel(risk) {
    const labels = {
        'no_spf': 'SPF Eksik',
        'dkim_missing': 'DKIM Eksik',
        'no_dkim': 'DKIM Eksik',  // Fallback
        'dkim_none': 'DKIM Eksik',  // Fallback
        'dmarc_none': 'DMARC Policy: None (Risk)',  // v1.1: More descriptive - DMARC record exists but policy is "none"
        'hosting_mx_weak': 'Hosting MX Zayıf',
        'spf_multiple_includes': 'SPF Çoklu Include'
    };
    return labels[risk] || risk.replace(/_/g, ' ').toUpperCase();
}

/**
 * Get signal tooltip text (Gün 3)
 */
function getSignalTooltip(signal) {
    const tooltips = {
        'spf': 'SPF (Sender Policy Framework) - Email gönderen sunucuları doğrular ve spam önleme sağlar',
        'dkim': 'DKIM (DomainKeys Identified Mail) - Email bütünlüğünü doğrular ve sahte email gönderimini önler',
        'dmarc_quarantine': 'DMARC Quarantine - Şüpheli emailler karantinaya alınır',
        'dmarc_reject': 'DMARC Reject - Şüpheli emailler reddedilir (en güvenli)',
        'dmarc_none': 'DMARC None - DMARC politikası yok (risk)'
    };
    return tooltips[signal] || '';
}

/**
 * Get risk tooltip text (Gün 3)
 */
function getRiskTooltip(risk) {
    const tooltips = {
        'no_spf': 'SPF kaydı eksik - Email sahteciliği riski',
        'dkim_missing': 'DKIM kaydı eksik - Email bütünlüğü doğrulanamıyor',
        'dmarc_none': 'DMARC politikası yok - Email güvenliği zayıf',
        'hosting_mx_weak': 'Hosting MX kayıtları zayıf - Email teslimat sorunları olabilir',
        'spf_multiple_includes': 'SPF çoklu include - Yapılandırma karmaşıklığı ve risk'
    };
    return tooltips[risk] || '';
}

/**
 * Show score breakdown modal (G19 - UI Patch v1.1)
 * Phase 1.2: Improved data flow - clear previous content, ensure correct domain/score
 */
export function showScoreBreakdown(breakdown, domain) {
    const modal = document.getElementById('score-breakdown-modal');
    const content = document.getElementById('score-breakdown-content');
    
    if (!modal || !content) {
        logError('Modal or content element not found', { modal, content });
        return;
    }
    
    // Phase 1.2: Clear previous content to prevent stale data
    content.innerHTML = '';
    
    // Phase 1.2: Validate domain matches breakdown data
    if (breakdown.domain && breakdown.domain !== domain) {
        warn('Domain mismatch:', { expected: domain, received: breakdown.domain });
    }
    
    log('Showing score breakdown for domain:', domain, breakdown);
    
    // Build HTML content
    let html = `<div class="score-breakdown">`;
    
    // v1.1: Modal header with explanation - Provider-specific description
    const provider = breakdown.provider?.name || null;
    let descriptionText = "Bu skor, DNS ve IP verilerine göre hesaplandı.";
    
    if (provider === "M365") {
        descriptionText = "Bu skor, M365 kullanımı, DNS ve IP verilerine göre hesaplandı.";
    } else if (provider === "Google") {
        descriptionText = "Bu skor, Google Workspace kullanımı, DNS ve IP verilerine göre hesaplandı.";
    } else if (provider === "Local" || provider === "Hosting") {
        descriptionText = "Bu skor, mevcut email sağlayıcınız, DNS ve IP verilerine göre hesaplandı.";
    } else if (provider && provider !== "Unknown") {
        descriptionText = `Bu skor, ${escapeHtml(provider)} kullanımı, DNS ve IP verilerine göre hesaplandı.`;
    }
    
    html += `<div class="score-breakdown__header" style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #e0e0e0;">
        <h2 style="margin: 0 0 0.5rem 0; font-size: 1.5rem; color: #333;">Neden bu skor?</h2>
        <p style="margin: 0; color: #666; font-size: 0.9rem; line-height: 1.5;">
            ${descriptionText}
        </p>
    </div>`;
    
    // Domain info
    html += `<div class="score-breakdown__section">
        <div class="score-breakdown__item">
            <span class="score-breakdown__label">Domain</span>
            <span class="score-breakdown__value">${escapeHtml(domain)}</span>
        </div>
    </div>`;
    
    // G20: Domain Intelligence (if available)
    if (breakdown.tenant_size || breakdown.local_provider || breakdown.dmarc_coverage !== undefined) {
        html += `<div class="score-breakdown__section">
            <div class="score-breakdown__section-title">Domain Intelligence (G20)</div>`;
        
        if (breakdown.tenant_size) {
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">Tenant Size</span>
                <span class="score-breakdown__value">${escapeHtml(breakdown.tenant_size)}</span>
            </div>`;
        }
        
        if (breakdown.local_provider) {
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">Local Provider</span>
                <span class="score-breakdown__value">${escapeHtml(breakdown.local_provider)}</span>
            </div>`;
        }
        
        // v1.1: Show DMARC Coverage or Policy based on policy value
        // If dmarc_policy is "none", show policy instead of coverage (coverage is misleading)
        if (breakdown.dmarc_coverage !== undefined && breakdown.dmarc_coverage !== null) {
            // Check if DMARC policy is "none" - if so, show policy instead of coverage
            const dmarcPolicy = breakdown.dmarc_policy;
            if (dmarcPolicy && dmarcPolicy.toLowerCase() === 'none') {
                // DMARC exists but policy is "none" - show policy instead of coverage
                html += `<div class="score-breakdown__item">
                    <span class="score-breakdown__label">DMARC Policy</span>
                    <span class="score-breakdown__value score-breakdown__value--negative">None (Risk)</span>
                </div>`;
            } else if (dmarcPolicy && (dmarcPolicy.toLowerCase() === 'quarantine' || dmarcPolicy.toLowerCase() === 'reject')) {
                // DMARC policy is quarantine or reject - show coverage
                html += `<div class="score-breakdown__item">
                    <span class="score-breakdown__label">DMARC Coverage</span>
                    <span class="score-breakdown__value">${breakdown.dmarc_coverage}%</span>
                </div>`;
            } else {
                // DMARC policy is unknown or null - show coverage as fallback
                html += `<div class="score-breakdown__item">
                    <span class="score-breakdown__label">DMARC Coverage</span>
                    <span class="score-breakdown__value">${breakdown.dmarc_coverage}%</span>
                </div>`;
            }
        } else if (breakdown.dmarc_policy) {
            // No coverage but policy exists - show policy
            const dmarcPolicy = breakdown.dmarc_policy;
            const policyClass = dmarcPolicy.toLowerCase() === 'none' ? 'score-breakdown__value--negative' : '';
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">DMARC Policy</span>
                <span class="score-breakdown__value ${policyClass}">${escapeHtml(dmarcPolicy)}${dmarcPolicy.toLowerCase() === 'none' ? ' (Risk)' : ''}</span>
            </div>`;
        }
        
        html += `</div>`;
    }
    
    // Base score
    html += `<div class="score-breakdown__section">
        <div class="score-breakdown__section-title">Temel Skor</div>
        <div class="score-breakdown__item">
            <span class="score-breakdown__label">Başlangıç Skoru</span>
            <span class="score-breakdown__value">${breakdown.base_score || 0}</span>
        </div>
    </div>`;
    
    // Provider points
    if (breakdown.provider) {
        html += `<div class="score-breakdown__section">
            <div class="score-breakdown__section-title">Provider</div>
            <div class="score-breakdown__item">
                <span class="score-breakdown__label">${escapeHtml(breakdown.provider.name || 'Unknown')}</span>
                <span class="score-breakdown__value score-breakdown__value--positive">+${breakdown.provider.points || 0}</span>
            </div>
        </div>`;
    }
    
    // Phase 1.2: Signal points (positive) - Fixed order: SPF → DKIM → DMARC
    // Order: SPF first, then DKIM, then DMARC variants (quarantine, reject)
    const signalOrder = ['spf', 'dkim', 'dmarc_quarantine', 'dmarc_reject'];
    if (breakdown.signal_points && Object.keys(breakdown.signal_points).length > 0) {
        html += `<div class="score-breakdown__section">
            <div class="score-breakdown__section-title">Pozitif Sinyaller</div>`;
        
        // Show in fixed order
        for (const signal of signalOrder) {
            if (breakdown.signal_points[signal] !== undefined) {
                const points = breakdown.signal_points[signal];
                // Skip dmarc_none if it's 0 (it's a neutral/negative signal)
                if (signal === 'dmarc_none' && points === 0) {
                    continue;
                }
                const label = getSignalLabel(signal);
                const tooltip = getSignalTooltip(signal);
                html += `<div class="score-breakdown__item">
                    <span class="score-breakdown__label" ${tooltip ? `data-tooltip="${escapeHtml(tooltip)}"` : ''}>${escapeHtml(label)}</span>
                    <span class="score-breakdown__value score-breakdown__value--positive">+${points}</span>
                </div>`;
            }
        }
        
        // Show any remaining signals not in fixed order (except dmarc_none with 0 points)
        for (const [signal, points] of Object.entries(breakdown.signal_points)) {
            if (!signalOrder.includes(signal) && !(signal === 'dmarc_none' && points === 0)) {
                const label = getSignalLabel(signal);
                const tooltip = getSignalTooltip(signal);
                html += `<div class="score-breakdown__item">
                    <span class="score-breakdown__label" ${tooltip ? `data-tooltip="${escapeHtml(tooltip)}"` : ''}>${escapeHtml(label)}</span>
                    <span class="score-breakdown__value score-breakdown__value--positive">+${points}</span>
                </div>`;
            }
        }
        html += `</div>`;
    }
    
    // Phase 1.2: Risk points (negative) - Fixed order: SPF risks → DKIM risks → DMARC risks → Other risks
    // Order: SPF-related risks first, then DKIM, then DMARC, then others
    const riskOrder = ['no_spf', 'spf_multiple_includes', 'dkim_missing', 'no_dkim', 'dkim_none', 'dmarc_none', 'hosting_mx_weak'];
    if (breakdown.risk_points && Object.keys(breakdown.risk_points).length > 0) {
        html += `<div class="score-breakdown__section">
            <div class="score-breakdown__section-title">Risk Faktörleri</div>`;
        
        // Merge no_dkim and dkim_none into single entry
        const mergedRiskPoints = { ...breakdown.risk_points };
        if (mergedRiskPoints.no_dkim !== undefined && mergedRiskPoints.dkim_none !== undefined) {
            const dkimTotal = mergedRiskPoints.no_dkim + mergedRiskPoints.dkim_none;
            delete mergedRiskPoints.no_dkim;
            delete mergedRiskPoints.dkim_none;
            mergedRiskPoints.dkim_missing = dkimTotal;
        }
        
        // Show in fixed order
        for (const risk of riskOrder) {
            if (mergedRiskPoints[risk] !== undefined) {
                const points = mergedRiskPoints[risk];
                const label = getRiskLabel(risk);
                const tooltip = getRiskTooltip(risk);
                html += `<div class="score-breakdown__item">
                    <span class="score-breakdown__label" ${tooltip ? `data-tooltip="${escapeHtml(tooltip)}"` : ''}>${escapeHtml(label)}</span>
                    <span class="score-breakdown__value score-breakdown__value--negative">${points}</span>
                </div>`;
            }
        }
        
        // Show any remaining risks not in fixed order
        for (const [risk, points] of Object.entries(mergedRiskPoints)) {
            if (!riskOrder.includes(risk)) {
                const label = getRiskLabel(risk);
                const tooltip = getRiskTooltip(risk);
                html += `<div class="score-breakdown__item">
                    <span class="score-breakdown__label" ${tooltip ? `data-tooltip="${escapeHtml(tooltip)}"` : ''}>${escapeHtml(label)}</span>
                    <span class="score-breakdown__value score-breakdown__value--negative">${points}</span>
                </div>`;
            }
        }
        html += `</div>`;
    }
    
    // Total score
    html += `<div class="score-breakdown__total">
        <span class="score-breakdown__total-label">Toplam Skor</span>
        <span class="score-breakdown__total-value">${breakdown.total_score || 0}</span>
    </div>`;
    
    // Phase 3: P-Model Fields (CSP P-Model)
    if (breakdown.technical_heat || breakdown.commercial_segment || breakdown.commercial_heat || breakdown.priority_category || breakdown.priority_label) {
        html += `<div class="score-breakdown__section" style="margin-top: 1.5rem; border-top: 2px solid #e0e0e0; padding-top: 1rem;">
            <div class="score-breakdown__section-title">CSP P-Model (Phase 3)</div>`;
        
        if (breakdown.technical_heat) {
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">Technical Heat</span>
                <span class="score-breakdown__value">${escapeHtml(breakdown.technical_heat)}</span>
            </div>`;
        }
        
        if (breakdown.commercial_segment) {
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">Commercial Segment</span>
                <span class="score-breakdown__value">${escapeHtml(breakdown.commercial_segment)}</span>
            </div>`;
        }
        
        if (breakdown.commercial_heat) {
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">Commercial Heat</span>
                <span class="score-breakdown__value">${escapeHtml(breakdown.commercial_heat)}</span>
            </div>`;
        }
        
        if (breakdown.priority_category) {
            const priorityBadge = getPriorityBadge(breakdown.priority_category);
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">Priority Category</span>
                <span class="score-breakdown__value">${priorityBadge}</span>
            </div>`;
        }
        
        if (breakdown.priority_label) {
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">Priority Label</span>
                <span class="score-breakdown__value">${escapeHtml(breakdown.priority_label)}</span>
            </div>`;
        }
        
        html += `</div>`;
    }
    
    // Gün 3: PDF Export button
    // IP Enrichment: Network & Location (Minimal UI)
    if (breakdown.ip_enrichment) {
        html += `<div class="score-breakdown__section" style="margin-top: 1rem; border-top: 1px solid #e5e7eb; padding-top: 1rem;">
            <div class="score-breakdown__section-title">Network & Location</div>`;
        
        // v1.1: Show location info more prominently
        if (breakdown.ip_enrichment.country) {
            const city = breakdown.ip_enrichment.city ? `, ${escapeHtml(breakdown.ip_enrichment.city)}` : '';
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">Konum</span>
                <span class="score-breakdown__value">${escapeHtml(breakdown.ip_enrichment.country)}${city} <span style="font-size: 0.85rem; color: #666;">(IP bazlı tahmin)</span></span>
            </div>`;
        }
        
        if (breakdown.ip_enrichment.is_proxy) {
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">⚠️ Proxy Warning</span>
                <span class="score-breakdown__value score-breakdown__value--negative">Proxy detected${breakdown.ip_enrichment.proxy_type ? ` (${escapeHtml(breakdown.ip_enrichment.proxy_type)})` : ''}</span>
            </div>`;
        }
        
        html += `</div>`;
    }

    html += `<div class="score-breakdown__section" style="margin-top: 1rem;">
        <button type="button" id="btn-export-pdf" class="form__button" style="width: 100%;">
            📄 PDF İndir
        </button>
    </div>`;
    
    html += `</div>`;
    
    content.innerHTML = html;
    modal.style.display = 'block';
    
    // Gün 3: Bind PDF export button
    const pdfButton = document.getElementById('btn-export-pdf');
    if (pdfButton) {
        pdfButton.addEventListener('click', async () => {
            try {
                const { exportPDF } = await import('./api.js');
                await exportPDF(domain);
            } catch (error) {
                logError('PDF export error:', error);
            }
        });
    }
}

/**
 * Hide score breakdown modal (G19)
 */
export function hideScoreBreakdown() {
    const modal = document.getElementById('score-breakdown-modal');
    if (modal) {
        modal.style.display = 'none';
    }
    // Phase 1.2: Hide loading state when modal closes
    hideScoreModalLoading();
}

/**
 * Show score breakdown modal loading state (Phase 1.2)
 */
export function showScoreModalLoading() {
    const loading = document.getElementById('score-modal-loading');
    const content = document.getElementById('score-breakdown-content');
    if (loading) {
        loading.classList.remove('hidden');
    }
    if (content) {
        content.classList.add('hidden');
    }
}

/**
 * Hide score breakdown modal loading state (Phase 1.2)
 */
export function hideScoreModalLoading() {
    const loading = document.getElementById('score-modal-loading');
    const content = document.getElementById('score-breakdown-content');
    if (loading) {
        loading.classList.add('hidden');
    }
    if (content) {
        content.classList.remove('hidden');
    }
}

/**
 * Show sales summary modal (G21 Phase 2 + v1.1 Intelligence Layer)
 * 
 * @param {import('../types/sales.js').SalesSummary} summary - Sales summary response from API
 * @param {string} domain - Domain name
 */
export function showSalesSummary(summary, domain) {
    const modal = document.getElementById('sales-summary-modal');
    const content = document.getElementById('sales-summary-content');
    
    if (!modal || !content) {
        logError('Sales summary modal or content element not found', { modal, content });
        return;
    }
    
    content.innerHTML = '';
    
    log('Showing sales summary for domain:', domain, summary);
    
    // Build HTML content
    let html = `<div class="sales-summary">`;
    
    // One-liner
    html += `<div class="sales-summary__section">
        <div class="sales-summary__section-title">Özet</div>
        <div class="sales-summary__one-liner">${escapeHtml(summary.one_liner || 'N/A')}</div>
    </div>`;
    
    // Segment Explanation (v1.1)
    if (summary.segment_explanation) {
        html += `<div class="sales-summary__section">
            <div class="sales-summary__section-title">Segment Açıklaması</div>
            <div class="sales-summary__explanation">
                ${escapeHtml(summary.segment_explanation)}
            </div>
        </div>`;
    }
    
    // Provider Reasoning (v1.1)
    if (summary.provider_reasoning) {
        html += `<div class="sales-summary__section">
            <div class="sales-summary__section-title">Mevcut Sağlayıcı Değerlendirmesi</div>
            <div class="sales-summary__explanation">
                ${escapeHtml(summary.provider_reasoning)}
            </div>
        </div>`;
    }
    
    // Security Reasoning (v1.1)
    if (summary.security_reasoning) {
        const security = summary.security_reasoning;
        const riskClass = security.risk_level === 'high' ? 'high' : security.risk_level === 'medium' ? 'medium' : 'low';
        const riskLabel = security.risk_level === 'high' ? 'YÜKSEK RİSK' : security.risk_level === 'medium' ? 'ORTA RİSK' : 'DÜŞÜK RİSK';
        html += `<div class="sales-summary__section">
            <div class="sales-summary__section-title">Güvenlik Değerlendirmesi</div>
            <div class="sales-summary__security-reasoning sales-summary__security-reasoning--${riskClass}">
                <div class="sales-summary__security-header">
                    <span class="sales-summary__security-risk-badge sales-summary__security-risk-badge--${riskClass}">
                        ${escapeHtml(riskLabel)}
                    </span>
                </div>
                <div class="sales-summary__security-summary-block">
                    <div class="sales-summary__security-summary-label">Risk Özeti:</div>
                    <div class="sales-summary__security-summary">${escapeHtml(security.summary)}</div>
                </div>
                <div class="sales-summary__security-details">
                    <div class="sales-summary__security-details-title">Teknik Durum:</div>
                    <ul class="sales-summary__security-details-list">
                        ${security.details.map(detail => `<li>${escapeHtml(detail)}</li>`).join('')}
                    </ul>
                </div>
                <div class="sales-summary__security-sales-angle">
                    <div class="sales-summary__security-sales-angle-label"><strong>Satış Açısı:</strong></div>
                    <div class="sales-summary__security-sales-angle-text">${escapeHtml(security.sales_angle)}</div>
                </div>
                <div class="sales-summary__security-action">
                    <div class="sales-summary__security-action-label"><strong>Önerilen Aksiyon:</strong></div>
                    <div class="sales-summary__security-action-text">${escapeHtml(security.recommended_action)}</div>
                </div>
            </div>
        </div>`;
    }
    
    // Call script
    if (summary.call_script && summary.call_script.length > 0) {
        html += `<div class="sales-summary__section">
            <div class="sales-summary__section-title">Call Script</div>
            <div class="sales-summary__call-script">
                ${summary.call_script.map((item, idx) => 
                    `<div class="sales-summary__call-script-item">
                        <span class="sales-summary__bullet">•</span>
                        <span class="sales-summary__text">${escapeHtml(item)}</span>
                    </div>`
                ).join('')}
            </div>
        </div>`;
    }
    
    // Discovery questions
    if (summary.discovery_questions && summary.discovery_questions.length > 0) {
        html += `<div class="sales-summary__section">
            <div class="sales-summary__section-title">Discovery Questions</div>
            <div class="sales-summary__questions">
                ${summary.discovery_questions.map((item, idx) => 
                    `<div class="sales-summary__question-item">
                        <span class="sales-summary__question-number">${idx + 1}.</span>
                        <span class="sales-summary__text">${escapeHtml(item)}</span>
                    </div>`
                ).join('')}
            </div>
        </div>`;
    }
    
    // Offer tier
    if (summary.offer_tier) {
        const tier = summary.offer_tier;
        html += `<div class="sales-summary__section">
            <div class="sales-summary__section-title">Offer Tier</div>
            <div class="sales-summary__offer-tier">
                <div class="sales-summary__offer-tier-name">${escapeHtml(tier.tier || 'N/A')}</div>
                <div class="sales-summary__offer-tier-details">
                    <div class="sales-summary__offer-tier-item">
                        <span class="sales-summary__label">Fiyat (kullanıcı/ay):</span>
                        <span class="sales-summary__value">€${tier.price_per_user_per_month || 0}</span>
                    </div>
                    ${tier.migration_fee ? `
                    <div class="sales-summary__offer-tier-item">
                        <span class="sales-summary__label">Migration Ücreti:</span>
                        <span class="sales-summary__value">€${tier.migration_fee}</span>
                    </div>
                    ` : ''}
                    ${tier.defender_price_per_user_per_month ? `
                    <div class="sales-summary__offer-tier-item">
                        <span class="sales-summary__label">Defender (kullanıcı/ay):</span>
                        <span class="sales-summary__value">€${tier.defender_price_per_user_per_month}</span>
                    </div>
                    ` : ''}
                    ${tier.consulting_fee ? `
                    <div class="sales-summary__offer-tier-item">
                        <span class="sales-summary__label">Consulting Ücreti:</span>
                        <span class="sales-summary__value">€${tier.consulting_fee}</span>
                    </div>
                    ` : ''}
                </div>
                ${tier.recommendation ? `
                <div class="sales-summary__offer-tier-recommendation">
                    ${escapeHtml(tier.recommendation)}
                </div>
                ` : ''}
            </div>
        </div>`;
    }
    
    // Opportunity potential & urgency
    html += `<div class="sales-summary__section">
        <div class="sales-summary__section-title">Fırsat Analizi</div>
        <div class="sales-summary__metrics">
            <div class="sales-summary__metric">
                <span class="sales-summary__label">Opportunity Potential:</span>
                <span class="sales-summary__value sales-summary__value--${getOpportunityClass(summary.opportunity_potential)}">
                    ${summary.opportunity_potential || 0}/100
                </span>
            </div>
            <div class="sales-summary__metric">
                <span class="sales-summary__label">Urgency:</span>
                <span class="sales-summary__value sales-summary__value--${summary.urgency || 'low'}">
                    ${escapeHtml((summary.urgency || 'low').toUpperCase())}
                </span>
            </div>
        </div>`;
    
    // Opportunity Rationale (v1.1) - Breakdown
    if (summary.opportunity_rationale) {
        const rationale = summary.opportunity_rationale;
        html += `<div class="sales-summary__opportunity-rationale">
            <div class="sales-summary__opportunity-rationale-title">Neden ${rationale.total} puan?</div>
            <div class="sales-summary__opportunity-rationale-summary">${escapeHtml(rationale.summary)}</div>
            <div class="sales-summary__opportunity-factors">
                ${rationale.factors.map(factor => `
                    <div class="sales-summary__opportunity-factor">
                        <div class="sales-summary__opportunity-factor-header">
                            <span class="sales-summary__opportunity-factor-name">${escapeHtml(factor.name)}</span>
                            <span class="sales-summary__opportunity-factor-score">${factor.score} puan</span>
                        </div>
                        <div class="sales-summary__opportunity-factor-details">
                            <span class="sales-summary__opportunity-factor-raw">Değer: ${escapeHtml(String(factor.raw))}</span>
                            <span class="sales-summary__opportunity-factor-comment">${escapeHtml(factor.comment)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>`;
    }
    
    html += `</div>`;
    
    // Next Step CTA (v1.1)
    if (summary.next_step) {
        const nextStep = summary.next_step;
        const actionClass = nextStep.action === 'call' ? 'call' : nextStep.action === 'email' ? 'email' : nextStep.action === 'nurture' ? 'nurture' : 'wait';
        const priorityClass = nextStep.priority === 'high' ? 'high' : nextStep.priority === 'medium' ? 'medium' : 'low';
        const actionLabel = nextStep.action === 'call' ? 'ARAMA' : nextStep.action === 'email' ? 'E-POSTA' : nextStep.action === 'nurture' ? 'NURTURE' : 'BEKLE';
        const timelineLabel = nextStep.timeline === '24_saat' ? '24 saat içinde' : nextStep.timeline === '3_gün' ? '3 gün içinde' : nextStep.timeline === '1_hafta' ? '1 hafta içinde' : '1 ay içinde';
        const priorityLabel = nextStep.priority === 'high' ? 'Yüksek Öncelik' : nextStep.priority === 'medium' ? 'Orta Öncelik' : 'Düşük Öncelik';
        html += `<div class="sales-summary__section">
            <div class="sales-summary__section-title">Sonraki Adım</div>
            <div class="sales-summary__next-step sales-summary__next-step--${actionClass}">
                <div class="sales-summary__next-step-header">
                    <span class="sales-summary__next-step-action-badge sales-summary__next-step-action-badge--${actionClass}">
                        ${escapeHtml(actionLabel)}
                    </span>
                    <span class="sales-summary__next-step-timeline-badge">
                        ${escapeHtml(timelineLabel)}
                    </span>
                    <span class="sales-summary__next-step-priority-badge sales-summary__next-step-priority-badge--${priorityClass}">
                        ${escapeHtml(priorityLabel)}
                    </span>
                </div>
                <div class="sales-summary__next-step-message">
                    <strong>Müşteriye Mesaj:</strong> ${escapeHtml(nextStep.message)}
                </div>
                <div class="sales-summary__next-step-internal">
                    <strong>CRM Notu:</strong> ${escapeHtml(nextStep.internal_note)}
                </div>
            </div>
        </div>`;
    }
    
    html += `</div>`;
    
    content.innerHTML = html;
    modal.style.display = 'block';
}

/**
 * Get opportunity potential CSS class
 */
function getOpportunityClass(score) {
    if (score >= 70) return 'high';
    if (score >= 50) return 'medium';
    if (score >= 30) return 'low';
    return 'very-low';
}

/**
 * Show sales summary modal loading state
 */
export function showSalesModalLoading() {
    const loading = document.getElementById('sales-modal-loading');
    const content = document.getElementById('sales-summary-content');
    if (loading) {
        loading.classList.remove('hidden');
    }
    if (content) {
        content.classList.add('hidden');
    }
}

/**
 * Hide sales summary modal loading state
 */
export function hideSalesModalLoading() {
    const loading = document.getElementById('sales-modal-loading');
    const content = document.getElementById('sales-summary-content');
    if (loading) {
        loading.classList.add('hidden');
    }
    if (content) {
        content.classList.remove('hidden');
    }
}

/**
 * Hide sales summary modal (G21 Phase 2)
 */
export function hideSalesSummary() {
    const modal = document.getElementById('sales-summary-modal');
    if (modal) {
        modal.style.display = 'none';
    }
    hideSalesModalLoading();
}

/**
 * Show sales summary error in modal (G21 Phase 2)
 */
export function showSalesSummaryError(domain, errorMessage) {
    const modal = document.getElementById('sales-summary-modal');
    const content = document.getElementById('sales-summary-content');
    
    if (!modal || !content) return;
    
    const html = `
        <div class="sales-summary">
            <div class="sales-summary__section">
                <div class="sales-summary__item">
                    <span class="sales-summary__label">Domain</span>
                    <span class="sales-summary__value">${escapeHtml(domain)}</span>
                </div>
            </div>
            <div class="sales-summary__section" style="text-align: center; padding: 2rem;">
                <div style="color: #e74c3c; font-size: 1.125rem; margin-bottom: 1rem;">
                    ⚠️ ${escapeHtml(errorMessage)}
                </div>
                <p style="color: #666; margin-bottom: 1.5rem;">
                    Sales summary'yi görmek için önce domain'i taramanız gerekiyor.
                </p>
            </div>
        </div>
    `;
    
    content.innerHTML = html;
    modal.style.display = 'block';
}

/**
 * Show score breakdown error in modal (G19)
 */
export function showScoreBreakdownError(domain, errorMessage) {
    const modal = document.getElementById('score-breakdown-modal');
    const content = document.getElementById('score-breakdown-content');
    
    if (!modal || !content) return;
    
    // Build error HTML with scan option
    const html = `
        <div class="score-breakdown">
            <div class="score-breakdown__section">
                <div class="score-breakdown__item">
                    <span class="score-breakdown__label">Domain</span>
                    <span class="score-breakdown__value">${escapeHtml(domain)}</span>
                </div>
            </div>
            <div class="score-breakdown__section" style="text-align: center; padding: 2rem;">
                <div style="color: #e74c3c; font-size: 1.125rem; margin-bottom: 1rem;">
                    ⚠️ ${escapeHtml(errorMessage)}
                </div>
                <p style="color: #666; margin-bottom: 1.5rem;">
                    Skor detaylarını görmek için önce domain'i taramanız gerekiyor.
                </p>
                <button type="button" id="btn-scan-domain-modal" class="form__button" style="margin: 0 auto;">
                    Domain'i Tara
                </button>
            </div>
        </div>
    `;
    
    content.innerHTML = html;
    modal.style.display = 'block';
    
    // Bind scan button
    const scanButton = document.getElementById('btn-scan-domain-modal');
    if (scanButton) {
        scanButton.addEventListener('click', async () => {
            scanButton.disabled = true;
            scanButton.textContent = 'Taranıyor...';
            
            try {
                // Import scanDomain and fetchScoreBreakdown functions
                const { scanDomain } = await import('./api.js');
                const { fetchScoreBreakdown } = await import('./api.js');
                
                // Scan the domain
                const result = await scanDomain(domain);
                
                // Show loading state in modal
                const content = document.getElementById('score-breakdown-content');
                if (content) {
                    content.innerHTML = `
                        <div style="text-align: center; padding: 2rem;">
                            <div style="color: #27ae60; font-size: 1.125rem; margin-bottom: 1rem;">
                                ✅ Domain başarıyla tarandı!
                            </div>
                            <p style="color: #666; margin-bottom: 1rem;">
                                Skor detayları yükleniyor...
                            </p>
                        </div>
                    `;
                }
                
                // Wait a moment for the scan to complete in the database
                // Retry mechanism: try up to 5 times with increasing delays
                let breakdown = null;
                const maxRetries = 5;
                const initialDelay = 1500; // Start with 1.5 seconds
                
                for (let attempt = 0; attempt < maxRetries; attempt++) {
                    await new Promise(resolve => setTimeout(resolve, initialDelay + (attempt * 500)));
                    
                    try {
                        breakdown = await fetchScoreBreakdown(domain);
                        break; // Success, exit retry loop
                    } catch (error) {
                        // Update loading message
                        const content = document.getElementById('score-breakdown-content');
                        if (content && attempt < maxRetries - 1) {
                            content.innerHTML = `
                                <div style="text-align: center; padding: 2rem;">
                                    <div style="color: #27ae60; font-size: 1.125rem; margin-bottom: 1rem;">
                                        ✅ Domain başarıyla tarandı!
                                    </div>
                                    <p style="color: #666; margin-bottom: 1rem;">
                                        Skor detayları yükleniyor... (${attempt + 1}/${maxRetries})
                                    </p>
                                </div>
                            `;
                        }
                    }
                }
                
                // Display score breakdown if successfully fetched
                if (breakdown) {
                    showScoreBreakdown(breakdown, domain);
                    
                    // Show success notification on main page (above table)
                    const errorEl = document.getElementById('error');
                    if (errorEl) {
                        errorEl.textContent = `✅ Domain başarıyla tarandı! Skor: ${result.score || 'N/A'}, Segment: ${result.segment || 'N/A'}`;
                        errorEl.style.backgroundColor = '#d4edda';
                        errorEl.style.color = '#155724';
                        errorEl.style.border = '1px solid #c3e6cb';
                        errorEl.style.display = 'block';
                        errorEl.style.position = 'sticky';
                        errorEl.style.top = '0';
                        errorEl.style.zIndex = '1000';
                        errorEl.style.marginBottom = '1rem';
                        setTimeout(() => {
                            errorEl.style.display = 'none';
                        }, 10000); // Show for 10 seconds instead of 5
                    }
                } else {
                    // If breakdown fetch fails after all retries, show success message and close modal
                    hideScoreBreakdown();
                    const errorEl = document.getElementById('error');
                    if (errorEl) {
                        errorEl.textContent = `✅ Domain başarıyla tarandı! Skor: ${result.score || 'N/A'}, Segment: ${result.segment || 'N/A'}. Skor detayları birkaç saniye içinde hazır olacak.`;
                        errorEl.style.backgroundColor = '#d4edda';
                        errorEl.style.color = '#155724';
                        errorEl.style.border = '1px solid #c3e6cb';
                        errorEl.style.display = 'block';
                        errorEl.style.position = 'sticky';
                        errorEl.style.top = '0';
                        errorEl.style.zIndex = '1000';
                        errorEl.style.marginBottom = '1rem';
                        setTimeout(() => {
                            errorEl.style.display = 'none';
                        }, 10000); // Show for 10 seconds
                    }
                }
                
                // Refresh leads list - trigger custom event
                const refreshEvent = new CustomEvent('refreshLeads');
                window.dispatchEvent(refreshEvent);
            } catch (error) {
                showError(`Tarama hatası: ${error.message}`);
                scanButton.disabled = false;
                scanButton.textContent = "Domain'i Tara";
            }
        });
    }
}

