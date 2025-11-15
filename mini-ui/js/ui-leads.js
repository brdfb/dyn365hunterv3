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
        
        return `
            <tr class="leads-table__row">
                <td class="leads-table__cell">${priorityBadge}</td>
                <td class="leads-table__cell">${escapeHtml(lead.domain || '-')}</td>
                <td class="leads-table__cell">${escapeHtml(lead.canonical_name || '-')}</td>
                <td class="leads-table__cell">${escapeHtml(lead.provider || '-')}</td>
                <td class="leads-table__cell">
                    ${lead.segment ? `<span class="segment-badge segment-badge--${segmentClass}">${escapeHtml(lead.segment)}</span>` : '-'}
                </td>
                <td class="leads-table__cell ${scoreClass} ${lead.readiness_score !== null && lead.readiness_score !== undefined ? 'score-clickable' : ''}" 
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
        // Max score is not in KPIs endpoint, keep from legacy dashboard if available
        // Or fetch from legacy endpoint separately
        const maxScore = window.state.dashboard?.max_score;
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
 * Priority 3+ = • (medium/low)
 */
function getPriorityBadge(priority_score) {
    if (priority_score === null || priority_score === undefined) return '-';
    
    switch (priority_score) {
        case 1:
            return '🔥'; // Highest priority (Migration 80+)
        case 2:
            return '⭐'; // High priority (Migration 70-79)
        case 3:
        case 4:
        case 5:
        case 6:
        default:
            return '•'; // Medium/Low priority
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
    document.getElementById('loading').style.display = 'block';
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
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    document.getElementById('loading').style.display = 'none';
}

/**
 * Hide error message
 */
export function hideError() {
    document.getElementById('error').style.display = 'none';
}

/**
 * Show score breakdown modal (G19)
 */
export function showScoreBreakdown(breakdown, domain) {
    const modal = document.getElementById('score-breakdown-modal');
    const content = document.getElementById('score-breakdown-content');
    
    if (!modal || !content) return;
    
    // Build HTML content
    let html = `<div class="score-breakdown">`;
    
    // Domain info
    html += `<div class="score-breakdown__section">
        <div class="score-breakdown__item">
            <span class="score-breakdown__label">Domain</span>
            <span class="score-breakdown__value">${escapeHtml(domain)}</span>
        </div>
    </div>`;
    
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
    
    // Signal points (positive)
    if (breakdown.signal_points && Object.keys(breakdown.signal_points).length > 0) {
        html += `<div class="score-breakdown__section">
            <div class="score-breakdown__section-title">Pozitif Sinyaller</div>`;
        for (const [signal, points] of Object.entries(breakdown.signal_points)) {
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">${escapeHtml(signal.toUpperCase())}</span>
                <span class="score-breakdown__value score-breakdown__value--positive">+${points}</span>
            </div>`;
        }
        html += `</div>`;
    }
    
    // Risk points (negative)
    if (breakdown.risk_points && Object.keys(breakdown.risk_points).length > 0) {
        html += `<div class="score-breakdown__section">
            <div class="score-breakdown__section-title">Risk Faktörleri</div>`;
        for (const [risk, points] of Object.entries(breakdown.risk_points)) {
            html += `<div class="score-breakdown__item">
                <span class="score-breakdown__label">${escapeHtml(risk.replace(/_/g, ' ').toUpperCase())}</span>
                <span class="score-breakdown__value score-breakdown__value--negative">${points}</span>
            </div>`;
        }
        html += `</div>`;
    }
    
    // Total score
    html += `<div class="score-breakdown__total">
        <span class="score-breakdown__total-label">Toplam Skor</span>
        <span class="score-breakdown__total-value">${breakdown.total_score || 0}</span>
    </div>`;
    
    html += `</div>`;
    
    content.innerHTML = html;
    modal.style.display = 'block';
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

