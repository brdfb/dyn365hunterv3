// UI Leads - Table and filter rendering

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
        const priorityBadge = getPriorityBadge(lead.priority_score);
        const priorityTooltip = getPriorityTooltip(lead.priority_score, lead.segment, lead.readiness_score);
        
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
                <td class="leads-table__cell leads-table__cell--tenant-size" title="${lead.tenant_size ? `Tenant büyüklüğü: ${lead.tenant_size}` : ''}">
                    ${lead.tenant_size ? `<span class="tenant-size-badge tenant-size-badge--${lead.tenant_size}">${escapeHtml(lead.tenant_size)}</span>` : '-'}
                </td>
                <td class="leads-table__cell leads-table__cell--local-provider">
                    ${lead.local_provider ? escapeHtml(lead.local_provider) : '-'}
                </td>
                <td class="leads-table__cell leads-table__cell--segment">
                    ${lead.segment ? `<span class="segment-badge segment-badge--${segmentClass}">${escapeHtml(lead.segment)}</span>` : '-'}
                </td>
                <td class="leads-table__cell leads-table__cell--score ${scoreClass} ${lead.readiness_score !== null && lead.readiness_score !== undefined ? 'score-clickable' : ''}" 
                    ${lead.readiness_score !== null && lead.readiness_score !== undefined ? `data-domain="${escapeHtml(lead.domain)}"` : ''}>
                    ${lead.readiness_score !== null && lead.readiness_score !== undefined ? lead.readiness_score : '-'}
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
 * Get priority badge (visual indicator)
 * Priority 1 = 🔥 (highest)
 * Priority 2 = ⭐ (high)
 * Priority 3 = 🟡 (medium-high)
 * Priority 4 = 🟠 (medium)
 * Priority 5 = ⚪ (low-medium)
 * Priority 6 = ⚫ (low)
 * Priority 7 = 🔴 (lowest)
 */
function getPriorityBadge(priority_score) {
    if (priority_score === null || priority_score === undefined) return '-';
    
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
            return '•'; // Unknown
    }
}

/**
 * Get priority tooltip text
 */
function getPriorityTooltip(priority_score, segment, score) {
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
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show loading indicator
 */
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
export function showError(message) {
    const errorEl = document.getElementById('error');
    if (!errorEl) return;
    
    errorEl.textContent = message;
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
        'dmarc_none': 'DMARC Yok (Risk)',
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
 */
export function showScoreBreakdown(breakdown, domain) {
    const modal = document.getElementById('score-breakdown-modal');
    const content = document.getElementById('score-breakdown-content');
    
    if (!modal || !content) {
        console.error('Modal or content element not found', { modal, content });
        return;
    }
    
    console.log('Showing score breakdown for domain:', domain, breakdown);
    
    // Build HTML content
    let html = `<div class="score-breakdown">`;
    
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
        
        if (breakdown.dmarc_coverage !== undefined && breakdown.dmarc_coverage !== null) {
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">DMARC Coverage</span>
                <span class="score-breakdown__value">${breakdown.dmarc_coverage}%</span>
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
    
    // Signal points (positive) - Fixed order and filter dmarc_none if 0
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
    
    // Risk points (negative) - Merge DKIM risks and fixed order
    const riskOrder = ['no_spf', 'dkim_missing', 'no_dkim', 'dkim_none', 'dmarc_none', 'hosting_mx_weak', 'spf_multiple_includes'];
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
    
    // Gün 3: PDF Export button
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
                console.error('PDF export error:', error);
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

