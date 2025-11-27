// UI Referrals - Referral inbox table and filter rendering (Phase 2)

import { log, warn, error as logError } from './logger.js';
import { escapeHtml } from './utils.js';

/**
 * Render referrals table
 */
export function renderReferralsTable(referrals) {
    const tbody = document.getElementById('referrals-table-body');
    const emptyState = document.getElementById('referrals-empty-state');
    const tableWrapper = document.getElementById('referrals-table-wrapper');
    
    if (!tbody) {
        logError('Referrals table body not found');
        return;
    }
    
    if (!referrals || referrals.length === 0) {
        tbody.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        if (tableWrapper) tableWrapper.style.display = 'none';
        return;
    }
    
    if (emptyState) emptyState.style.display = 'none';
    if (tableWrapper) tableWrapper.style.display = 'block';
    
    tbody.innerHTML = referrals.map(referral => {
        const linkStatusBadge = getLinkStatusBadge(referral.link_status);
        const referralTypeBadge = getReferralBadge(referral.referral_type);
        const statusBadge = getStatusBadge(referral.status);
        
        const companyName = referral.company_name || referral.customer_name || '-';
        return `
            <tr class="leads-table__row">
                <td class="leads-table__cell leads-table__cell--company" title="${companyName !== '-' ? escapeHtml(companyName) : ''}">
                    ${escapeHtml(companyName)}
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
                    <button type="button" class="referral-action-button referral-action-button--detail" data-referral-id="${escapeHtml(referral.referral_id)}" title="Detayları göster">🔍 Detay</button>
                    ${referral.link_status === 'unlinked' || !referral.link_status || referral.link_status === 'none'
                        ? `<button type="button" class="referral-action-button referral-action-button--link" data-referral-id="${escapeHtml(referral.referral_id)}" data-domain="${referral.domain ? escapeHtml(referral.domain) : ''}" title="Link to existing lead">🔗 Link</button>
                           ${referral.domain ? `<button type="button" class="referral-action-button referral-action-button--create" data-referral-id="${escapeHtml(referral.referral_id)}" title="Create lead from referral">➕ Create Lead</button>` : ''}`
                        : referral.link_status === 'auto_linked' || referral.link_status === 'linked'
                        ? `<span style="color: #27ae60; font-size: 0.875rem;">✓ Linked</span>`
                        : referral.link_status === 'multi_candidate' || referral.link_status === 'mixed'
                        ? `<span style="color: #f39c12; font-size: 0.875rem;">Multiple</span>`
                        : '-'
                    }
                </td>
            </tr>
        `;
    }).join('');
}

const REFERRAL_DETAIL_SELECTORS = {
    modal: 'referral-detail-modal',
    content: 'referral-detail-content',
    error: 'referral-detail-error',
    loading: 'referral-detail-loading',
};

export function openReferralDetailModal() {
    const modal = document.getElementById(REFERRAL_DETAIL_SELECTORS.modal);
    const errorEl = document.getElementById(REFERRAL_DETAIL_SELECTORS.error);
    const content = document.getElementById(REFERRAL_DETAIL_SELECTORS.content);
    if (modal) {
        modal.style.display = 'block';
    }
    if (errorEl) {
        errorEl.style.display = 'none';
        errorEl.textContent = '';
    }
    if (content) {
        content.innerHTML = '';
    }
}

export function closeReferralDetailModal() {
    const modal = document.getElementById(REFERRAL_DETAIL_SELECTORS.modal);
    if (modal) {
        modal.style.display = 'none';
    }
}

export function setReferralDetailLoading(isLoading) {
    const loadingEl = document.getElementById(REFERRAL_DETAIL_SELECTORS.loading);
    if (!loadingEl) return;
    loadingEl.classList.toggle('hidden', !isLoading);
}

export function setReferralDetailError(message) {
    const errorEl = document.getElementById(REFERRAL_DETAIL_SELECTORS.error);
    if (!errorEl) return;
    if (message) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    } else {
        errorEl.style.display = 'none';
        errorEl.textContent = '';
    }
}

export function renderReferralDetail(detail) {
    const content = document.getElementById(REFERRAL_DETAIL_SELECTORS.content);
    if (!content) return;

    const contact = detail.contact || {};
    const deal = detail.deal || {};
    const teamMembers = detail.team_members || [];

    const formatValue = (value) => value ? escapeHtml(String(value)) : '<span class="referral-detail__muted">-</span>';

    const teamHtml = teamMembers.length
        ? `<ul class="referral-detail__team">
                ${teamMembers.map(member => `
                    <li>
                        <strong>${formatValue(member.name || '-')}</strong>
                        ${member.role ? `<span class="referral-detail__muted">(${escapeHtml(member.role)})</span>` : ''}
                        ${member.email ? `<br><a href="mailto:${escapeHtml(member.email)}">${escapeHtml(member.email)}</a>` : ''}
                        ${member.phone ? `<br><span>${escapeHtml(member.phone)}</span>` : ''}
                    </li>
                `).join('')}
           </ul>`
        : '<p class="referral-detail__muted">Takım üyesi bilgisi yok.</p>';

    const rawJson = detail.raw_data
        ? `<pre class="referral-detail__json">${escapeHtml(JSON.stringify(detail.raw_data, null, 2))}</pre>`
        : '<p class="referral-detail__muted">Ham JSON verisi dahil edilmedi.</p>';

    const syncedAt = detail.synced_at
        ? new Date(detail.synced_at).toLocaleString('tr-TR')
        : null;

    const estimatedValueDisplay = (() => {
        if (deal.estimated_value === null || deal.estimated_value === undefined) {
            return '<span class="referral-detail__muted">-</span>';
        }
        const numericValue = typeof deal.estimated_value === 'number'
            ? deal.estimated_value
            : parseFloat(deal.estimated_value);
        if (!Number.isNaN(numericValue)) {
            return `${escapeHtml(numericValue.toLocaleString('tr-TR'))} ${escapeHtml(deal.currency || detail.currency || 'USD')}`;
        }
        return escapeHtml(String(deal.estimated_value));
    })();

    // Build action buttons
    const emailToCopy = contact.email || (teamMembers.length > 0 ? teamMembers[0].email : null);
    const domainToCopy = detail.domain || detail.raw_domain;
    const dealValueToCopy = deal.estimated_value 
        ? `${deal.estimated_value.toLocaleString('tr-TR')} ${deal.currency || detail.currency || 'USD'}`
        : null;
    
    const actionButtonsHtml = `
        <div class="referral-detail__actions" data-referral-id="${escapeHtml(detail.referral_id)}">
            <div class="referral-detail__actions-group">
                ${emailToCopy ? `<button type="button" class="referral-detail__action-btn referral-detail__action-btn--copy" data-copy-value="${escapeHtml(emailToCopy)}" title="E-posta adresini kopyala">
                    📧 E-posta
                </button>` : ''}
                ${domainToCopy ? `<button type="button" class="referral-detail__action-btn referral-detail__action-btn--copy" data-copy-value="${escapeHtml(domainToCopy)}" title="Domain'i kopyala">
                    🌐 Domain
                </button>` : ''}
                ${dealValueToCopy ? `<button type="button" class="referral-detail__action-btn referral-detail__action-btn--copy" data-copy-value="${escapeHtml(dealValueToCopy)}" title="Deal değerini kopyala">
                    💰 Deal Value
                </button>` : ''}
                <button type="button" class="referral-detail__action-btn referral-detail__action-btn--copy" data-copy-value="${escapeHtml(detail.referral_id)}" title="Referral ID'yi kopyala">
                    🆔 Referral ID
                </button>
            </div>
            <div class="referral-detail__actions-group">
                <button type="button" class="referral-detail__action-btn referral-detail__action-btn--d365" disabled title="Dynamics 365 entegrasyonu yakında">
                    📤 Send to Dynamics
                </button>
                <a href="https://partner.microsoft.com/en-us/dashboard/referrals/${escapeHtml(detail.referral_id)}" target="_blank" rel="noopener noreferrer" class="referral-detail__action-btn referral-detail__action-btn--link" title="Partner Center'da aç">
                    🔗 Open in PC
                </a>
            </div>
        </div>
    `;

    content.innerHTML = `
        <div class="referral-detail">
            <div class="referral-detail__header">
                <div>
                    <h3>${escapeHtml(detail.company_name || detail.customer_name || 'İsimsiz Referral')}</h3>
                    <p class="referral-detail__muted">Referral ID: ${escapeHtml(detail.referral_id)}</p>
                </div>
                <div class="referral-detail__badges">
                    ${getReferralBadge(detail.referral_type)}
                    ${getStatusBadge(detail.status)}
                    ${detail.substatus ? `<span class="referral-detail__chip">${escapeHtml(detail.substatus)}</span>` : ''}
                </div>
            </div>
            ${actionButtonsHtml}

            <div class="referral-detail__grid">
                <section class="referral-detail__section">
                    <h4>Müşteri</h4>
                    <dl>
                        <div><dt>Şirket</dt><dd>${formatValue(detail.company_name || detail.customer_name)}</dd></div>
                        <div><dt>Ülke</dt><dd>${formatValue(detail.customer_country)}</dd></div>
                        <div><dt>Organizasyon</dt><dd>${formatValue(detail.organization_size)}</dd></div>
                        <div><dt>Domain</dt><dd>${formatValue(detail.domain || detail.raw_domain)}</dd></div>
                        <div><dt>Direction</dt><dd>${formatValue(detail.direction)}</dd></div>
                        <div><dt>Link Status</dt><dd>${formatValue(detail.link_status)}</dd></div>
                        <div><dt>Synced At</dt><dd>${syncedAt ? escapeHtml(syncedAt) : '<span class="referral-detail__muted">-</span>'}</dd></div>
                    </dl>
                </section>

                <section class="referral-detail__section">
                    <h4>İlgili Kişi</h4>
                    ${!contact.name && !contact.email && teamMembers.length === 0
                        ? `<p class="referral-detail__muted" style="margin-bottom: 1rem; font-style: italic;">
                            Primary contact bilgisi Partner Center API'den gelmedi.
                        </p>`
                        : ''
                    }
                    <dl>
                        <div><dt>İsim</dt><dd>${formatValue(contact.name)}</dd></div>
                        <div><dt>E-posta</dt><dd>${contact.email ? `<a href="mailto:${escapeHtml(contact.email)}">${escapeHtml(contact.email)}</a>` : '<span class="referral-detail__muted">-</span>'}</dd></div>
                        <div><dt>Telefon</dt><dd>${formatValue(contact.phone)}</dd></div>
                        <div><dt>Ünvan</dt><dd>${formatValue(contact.title)}</dd></div>
                    </dl>
                </section>

                <section class="referral-detail__section">
                    <h4>Lead Detayları</h4>
                    <dl>
                        <div><dt>Lead Adı</dt><dd>${formatValue(deal.lead_name)}</dd></div>
                        <div><dt>Lead ID</dt><dd>${formatValue(deal.lead_id)}</dd></div>
                        <div><dt>Estimated Close</dt><dd>${formatValue(deal.estimated_close_date)}</dd></div>
                        <div><dt>Estimated Value</dt><dd>${estimatedValueDisplay}</dd></div>
                        <div><dt>Notlar</dt><dd>${formatValue(deal.notes)}</dd></div>
                    </dl>
                </section>
            </div>

            <section class="referral-detail__section">
                <h4>Team Members</h4>
                ${teamHtml}
            </section>

            <section class="referral-detail__section referral-detail__section--raw">
                <details>
                    <summary>Ham JSON Verisi</summary>
                    ${rawJson}
                </details>
            </section>
        </div>
    `;
}

function setupReferralDetailModal() {
    const modal = document.getElementById(REFERRAL_DETAIL_SELECTORS.modal);
    if (!modal) return;

    const closeBtn = document.getElementById('referral-detail-modal-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeReferralDetailModal);
    }

    const overlay = modal.querySelector('.modal__overlay');
    if (overlay) {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeReferralDetailModal();
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            closeReferralDetailModal();
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupReferralDetailModal);
} else {
    setupReferralDetailModal();
}

/**
 * Get link status badge
 */
function getLinkStatusBadge(linkStatus) {
    // Normalize: handle both raw values (from Referrals API) and normalized values (from Leads API)
    if (!linkStatus || linkStatus === 'none') {
        return '<span class="link-status-badge link-status-badge--none" title="Partner Center referral yok">-</span>';
    }
    
    const status = linkStatus.toLowerCase();
    let badgeClass = 'link-status-badge';
    let icon = '';
    let tooltip = '';
    
    // Handle both raw and normalized values for consistency
    switch (status) {
        case 'linked':
        case 'auto_linked':
            badgeClass += ' link-status-badge--linked';
            icon = '🔗';
            tooltip = 'Bu domain Partner Center referral\'ına bağlı';
            break;
        case 'unlinked':
            badgeClass += ' link-status-badge--unlinked';
            icon = '🔓';
            tooltip = 'Partner Center referral\'ı var ama lead ile linklenmemiş';
            break;
        case 'mixed':
        case 'multi_candidate':
            badgeClass += ' link-status-badge--mixed';
            icon = '🔀';
            tooltip = 'Bu domain için birden fazla referral var (farklı link durumları)';
            break;
        default:
            badgeClass += ' link-status-badge--none';
            tooltip = 'Partner Center referral durumu bilinmiyor';
    }
    
    return `<span class="${badgeClass}" title="${escapeHtml(tooltip)}">${icon}</span>`;
}

/**
 * Get referral type badge (reuse from ui-leads.js pattern)
 */
function getReferralBadge(referralType) {
    // Match Leads Tab badge rendering for consistency
    if (!referralType) return '-';
    
    const type = referralType.toLowerCase();
    const labels = {
        'co-sell': 'Co-sell',
        'marketplace': 'Marketplace',
        'solution-provider': 'SP'  // Match Leads Tab: short label
    };
    
    // Full descriptions for tooltips
    const descriptions = {
        'co-sell': 'Co-sell',
        'marketplace': 'Marketplace',
        'solution-provider': 'Solution Provider'
    };
    
    const label = labels[type] || referralType;
    const description = descriptions[type] || referralType;
    
    // CSS class uses the type as-is (co-sell, marketplace, solution-provider)
    const cssType = type;  // Already in correct format for CSS class
    const badgeClass = `referral-badge referral-badge--${cssType}`;
    
    return `<span class="${badgeClass}" title="Partner Center Referral: ${escapeHtml(description)}">${escapeHtml(label)}</span>`;
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

