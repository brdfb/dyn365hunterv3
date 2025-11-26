// UI Referrals - Referral inbox table and filter rendering (Phase 2)

import { log, warn, error as logError } from './logger.js';
import { escapeHtml } from './utils.js';

/**
 * Render referrals table
 */
export function renderReferralsTable(referrals) {
    const tbody = document.getElementById('referrals-table-body');
    const emptyState = document.getElementById('referrals-empty-state');
    
    if (!referrals || referrals.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    
    tbody.innerHTML = referrals.map(referral => {
        const linkStatusBadge = getLinkStatusBadge(referral.link_status);
        const referralTypeBadge = getReferralBadge(referral.referral_type);
        const statusBadge = getStatusBadge(referral.status);
        
        return `
            <tr class="leads-table__row">
                <td class="leads-table__cell">
                    ${escapeHtml(referral.company_name || referral.customer_name || '-')}
                </td>
                <td class="leads-table__cell leads-table__cell--domain">
                    ${referral.domain ? escapeHtml(referral.domain) : '<span style="color: #999; font-style: italic;">Domain yok</span>'}
                    ${referral.raw_domain && referral.raw_domain !== referral.domain ? `<br><small style="color: #666;">Raw: ${escapeHtml(referral.raw_domain)}</small>` : ''}
                </td>
                <td class="leads-table__cell leads-table__cell--referral">
                    ${referralTypeBadge}
                </td>
                <td class="leads-table__cell">
                    ${statusBadge}
                    ${referral.substatus ? `<br><small style="color: #666;">${escapeHtml(referral.substatus)}</small>` : ''}
                </td>
                <td class="leads-table__cell">
                    ${linkStatusBadge}
                </td>
                <td class="leads-table__cell">
                    ${referral.deal_value ? `${escapeHtml(referral.deal_value.toLocaleString('tr-TR'))} ${referral.currency || 'USD'}` : '-'}
                </td>
                <td class="leads-table__cell">
                    ${referral.synced_at ? new Date(referral.synced_at).toLocaleString('tr-TR') : '-'}
                </td>
                <td class="leads-table__cell leads-table__cell--actions">
                    ${referral.link_status === 'unlinked' 
                        ? `<button type="button" class="referral-action-button referral-action-button--link" data-referral-id="${escapeHtml(referral.referral_id)}" data-domain="${referral.domain ? escapeHtml(referral.domain) : ''}" title="Link to existing lead">🔗 Link</button>
                           ${referral.domain ? `<button type="button" class="referral-action-button referral-action-button--create" data-referral-id="${escapeHtml(referral.referral_id)}" title="Create lead from referral">➕ Create Lead</button>` : ''}`
                        : referral.link_status === 'auto_linked'
                        ? `<span style="color: #27ae60; font-size: 0.875rem;">✓ Linked</span>`
                        : '-'
                    }
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Get link status badge
 */
function getLinkStatusBadge(linkStatus) {
    if (!linkStatus) {
        return '<span style="color: #999; font-style: italic;">Not set</span>';
    }
    
    switch (linkStatus) {
        case 'auto_linked':
            return '<span class="link-status-badge link-status-badge--linked" title="Linked to Hunter lead">✓ Linked</span>';
        case 'unlinked':
            return '<span class="link-status-badge link-status-badge--unlinked" title="Not linked to any Hunter lead">Unlinked</span>';
        case 'multi_candidate':
            return '<span class="link-status-badge link-status-badge--multi" title="Multiple candidate leads found">Multiple</span>';
        default:
            return escapeHtml(linkStatus);
    }
}

/**
 * Get referral type badge (reuse from ui-leads.js pattern)
 */
function getReferralBadge(referralType) {
    if (!referralType) return '-';
    
    const badgeClass = {
        'co-sell': 'referral-badge referral-badge--co-sell',
        'marketplace': 'referral-badge referral-badge--marketplace',
        'solution-provider': 'referral-badge referral-badge--solution-provider'
    }[referralType] || 'referral-badge';
    
    const label = {
        'co-sell': 'Co-sell',
        'marketplace': 'Marketplace',
        'solution-provider': 'Solution Provider'
    }[referralType] || referralType;
    
    return `<span class="${badgeClass}" title="Partner Center Referral: ${escapeHtml(label)}">${escapeHtml(label)}</span>`;
}

/**
 * Get status badge
 */
function getStatusBadge(status) {
    if (!status) return '-';
    
    const statusClass = {
        'Active': 'status-badge status-badge--active',
        'New': 'status-badge status-badge--new',
        'Closed': 'status-badge status-badge--closed'
    }[status] || 'status-badge';
    
    return `<span class="${statusClass}">${escapeHtml(status)}</span>`;
}

/**
 * Render referral pagination
 */
export function renderReferralPagination(pagination) {
    const paginationEl = document.getElementById('referrals-pagination');
    const infoEl = document.getElementById('referrals-pagination-info');
    const pagesEl = document.getElementById('referrals-pagination-pages');
    const prevBtn = document.getElementById('btn-referrals-prev');
    const nextBtn = document.getElementById('btn-referrals-next');
    
    if (!pagination || pagination.total === 0) {
        paginationEl.style.display = 'none';
        return;
    }
    
    paginationEl.style.display = 'flex';
    
    const totalPages = Math.ceil(pagination.total / pagination.page_size);
    const currentPage = pagination.page || 1;
    
    // Update info
    const start = (currentPage - 1) * pagination.page_size + 1;
    const end = Math.min(currentPage * pagination.page_size, pagination.total);
    infoEl.textContent = `${start}-${end} / ${pagination.total}`;
    
    // Update buttons
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
    
    // Render page numbers
    pagesEl.innerHTML = '';
    const maxPages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
    let endPage = Math.min(totalPages, startPage + maxPages - 1);
    
    if (endPage - startPage < maxPages - 1) {
        startPage = Math.max(1, endPage - maxPages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.type = 'button';
        pageBtn.className = `pagination__page ${i === currentPage ? 'pagination__page--active' : ''}`;
        pageBtn.textContent = i;
        pageBtn.dataset.page = i;
        pagesEl.appendChild(pageBtn);
    }
}

/**
 * Show/hide referral loading
 */
export function showReferralLoading() {
    const loadingEl = document.getElementById('referrals-loading');
    const tableLoadingEl = document.getElementById('referrals-table-loading');
    if (loadingEl) loadingEl.style.display = 'block';
    if (tableLoadingEl) tableLoadingEl.classList.remove('hidden');
}

export function hideReferralLoading() {
    const loadingEl = document.getElementById('referrals-loading');
    const tableLoadingEl = document.getElementById('referrals-table-loading');
    if (loadingEl) loadingEl.style.display = 'none';
    if (tableLoadingEl) tableLoadingEl.classList.add('hidden');
}

/**
 * Show/hide referral error
 */
export function showReferralError(message) {
    const errorEl = document.getElementById('referrals-error');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
}

export function hideReferralError() {
    const errorEl = document.getElementById('referrals-error');
    if (errorEl) {
        errorEl.style.display = 'none';
    }
}

