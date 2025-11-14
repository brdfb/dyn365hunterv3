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
                <td class="leads-table__cell ${scoreClass}">
                    ${lead.readiness_score !== null && lead.readiness_score !== undefined ? lead.readiness_score : '-'}
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Render dashboard stats (KPI area)
 */
export function renderStats(dashboard) {
    if (!dashboard) return;
    
    document.getElementById('kpi-total').textContent = dashboard.total_leads || 0;
    document.getElementById('kpi-migration').textContent = dashboard.migration || 0;
    
    // Display max score from backend
    const maxScore = dashboard.max_score !== null && dashboard.max_score !== undefined 
        ? dashboard.max_score 
        : '-';
    document.getElementById('kpi-max-score').textContent = maxScore;
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

