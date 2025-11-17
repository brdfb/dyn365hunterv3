// App - Global state, initialization, orchestration

import { fetchLeads, fetchKPIs, fetchDashboard, fetchScoreBreakdown, fetchSalesSummary } from './api.js';
import { renderLeadsTable, renderStats, renderKPIs, showLoading, hideLoading, showError, hideError, showScoreBreakdown, hideScoreBreakdown, showScoreBreakdownError, showScoreModalLoading, hideScoreModalLoading, setTableLoading, setFiltersLoading, setExportLoading, showSalesSummary, hideSalesSummary, showSalesSummaryError, showSalesModalLoading, hideSalesModalLoading } from './ui-leads.js';
import { bindCsvUploadForm, bindScanDomainForm } from './ui-forms.js';
import { log, warn, error as logError } from './logger.js';

// Global state (single object)
window.state = {
    leads: [],
    filters: {
        segment: '',
        minScore: null,
        provider: '',
        search: '',  // G19: Search query
        sortBy: null,  // G19: Sort field
        sortOrder: 'asc',  // G19: Sort order (asc/desc)
        page: 1,  // G19: Current page
        pageSize: 50  // G19: Items per page
    },
    pagination: {  // G19: Pagination metadata
        total: 0,
        page: 1,
        page_size: 50,
        total_pages: 0
    },
    dashboard: null,
    loading: false,
    // Modal cache - cache score breakdowns by domain to avoid duplicate API calls
    breakdownCache: {},  // { domain: breakdownData }
    // Pagination cache - prevent duplicate requests for same page/filters
    lastLeadsRequest: null  // { filters, timestamp } - track last request to prevent duplicates
};

/**
 * Initialize application
 */
async function init() {
    // Bind forms
    bindCsvUploadForm(refreshLeads);
    bindScanDomainForm(refreshLeads);
    
    // Bind filter button
    const btnFilter = document.getElementById('btn-filter');
    if (btnFilter) {
        btnFilter.addEventListener('click', applyFilters);
    }
    
    // Bind export buttons (Gün 3)
    const btnExportCsv = document.getElementById('btn-export-csv');
    const btnExportExcel = document.getElementById('btn-export-excel');
    if (btnExportCsv) {
        btnExportCsv.addEventListener('click', () => handleExport('csv'));
    }
    if (btnExportExcel) {
        btnExportExcel.addEventListener('click', () => handleExport('excel'));
    }
    
    // G19: Bind search input (debounced)
    // Phase 1.4: Save filter state on search
    const searchInput = document.getElementById('filter-search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                window.state.filters.search = e.target.value.trim();
                window.state.filters.page = 1; // Reset to first page on search
                // Phase 1.4: Save filter state on search
                saveFilterState();
                loadLeads();
            }, 400); // 400ms debounce (optimized for better UX)
        });
    }
    
    // Phase 1.4: Bind clear filters button
    const btnClearFilters = document.getElementById('btn-filters-clear');
    if (btnClearFilters) {
        btnClearFilters.addEventListener('click', clearFilters);
    }
    
    // G19: Bind table header sorting
    bindSortableHeaders();
    
    // G19: Bind pagination buttons
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    if (btnPrev) {
        btnPrev.addEventListener('click', () => {
            if (window.state.filters.page > 1) {
                window.state.filters.page--;
                loadLeads();
            }
        });
    }
    if (btnNext) {
        btnNext.addEventListener('click', () => {
            if (window.state.pagination.total_pages > window.state.filters.page) {
                window.state.filters.page++;
                loadLeads();
            }
        });
    }
    
    // G19: Bind score breakdown modal
    const modalClose = document.getElementById('modal-close');
    const modal = document.getElementById('score-breakdown-modal');
    if (modalClose) {
        modalClose.addEventListener('click', hideScoreBreakdown);
    }
    if (modal) {
        const overlay = modal.querySelector('.modal__overlay');
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                // Only close if clicking the overlay itself, not the content
                if (e.target === overlay) {
                    hideScoreBreakdown();
                }
            });
        }
        
        // Gün 3: ESC key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.style.display === 'block') {
                hideScoreBreakdown();
            }
        });
    }
    
    // G21 Phase 2: Bind sales summary modal
    const salesModalClose = document.getElementById('sales-modal-close');
    const salesModal = document.getElementById('sales-summary-modal');
    if (salesModalClose) {
        salesModalClose.addEventListener('click', hideSalesSummary);
    }
    if (salesModal) {
        const salesOverlay = salesModal.querySelector('.modal__overlay');
        if (salesOverlay) {
            salesOverlay.addEventListener('click', (e) => {
                if (e.target === salesOverlay) {
                    hideSalesSummary();
                }
            });
        }
        
        // ESC key to close sales modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && salesModal.style.display === 'block') {
                hideSalesSummary();
            }
        });
    }
    
    // G19: Bind score click handlers (delegated event listener)
    document.addEventListener('click', async (e) => {
        // Handle domain click - open website in new tab
        const domainCell = e.target.closest('.domain-clickable');
        if (domainCell) {
            const domain = domainCell.getAttribute('data-domain');
            if (domain && domain !== '-') {
                // Open domain website in new tab
                window.open(`https://${domain}`, '_blank', 'noopener,noreferrer');
                return;
            }
        }
        
        // Handle score click - show score breakdown
        const scoreCell = e.target.closest('.score-clickable');
        if (scoreCell) {
            const domain = scoreCell.getAttribute('data-domain');
            if (domain) {
                // Modal cache: Check if breakdown is already cached
                const cachedBreakdown = window.state.breakdownCache[domain];
                if (cachedBreakdown) {
                    // Use cached data - no API call needed
                    const modal = document.getElementById('score-breakdown-modal');
                    if (modal) {
                        modal.style.display = 'block';
                        showScoreBreakdown(cachedBreakdown, domain);
                    }
                    return;
                }
                
                // Phase 1.2: Open modal first, then show loading state inside modal
                const modal = document.getElementById('score-breakdown-modal');
                if (modal) {
                    modal.style.display = 'block';
                    // Phase 1.2: Show modal-specific loading state
                    showScoreModalLoading();
                }
                
                try {
                    const breakdown = await fetchScoreBreakdown(domain);
                    // Cache the breakdown for future use
                    window.state.breakdownCache[domain] = breakdown;
                    // Phase 1.2: Ensure we're showing the correct domain's breakdown
                    showScoreBreakdown(breakdown, domain);
                } catch (error) {
                    // Check if domain is not scanned
                    if (error.message.includes('henüz taranmamış') || error.message.includes('has not been scanned')) {
                        showScoreBreakdownError(domain, error.message);
                    } else {
                        showError(`Skor detayı yüklenemedi: ${error.message}`);
                        hideScoreBreakdown();
                    }
                } finally {
                    // Phase 1.2: Hide modal-specific loading state
                    hideScoreModalLoading();
                }
                return;
            }
        }
        
        // G21 Phase 2: Handle Sales button click - show sales summary
        const salesButton = e.target.closest('.sales-button');
        if (salesButton) {
            const domain = salesButton.getAttribute('data-domain');
            if (domain) {
                // Open modal first, then show loading state
                const modal = document.getElementById('sales-summary-modal');
                if (modal) {
                    modal.style.display = 'block';
                    showSalesModalLoading();
                }
                
                try {
                    const summary = await fetchSalesSummary(domain);
                    showSalesSummary(summary, domain);
                } catch (error) {
                    logError('Failed to fetch sales summary:', error);
                    showSalesSummaryError(domain, error.message);
                } finally {
                    hideSalesModalLoading();
                }
                return;
            }
        }
    });
    
    // Listen for refresh events
    window.addEventListener('refreshLeads', () => {
        setTimeout(() => loadLeads(), 1000);
    });
    
    // Phase 1.4: Restore filter state from localStorage before loading
    restoreFilterState();
    
    // Load initial data
    await loadKPIs();  // G19: Use new KPIs endpoint
    await loadLeads();
}

/**
 * Load dashboard KPIs (G19 - New endpoint)
 */
async function loadKPIs() {
    try {
        // Fetch KPIs from new endpoint
        const kpis = await fetchKPIs();
        window.state.kpis = kpis;
        
        // Also fetch legacy dashboard for max_score (not in KPIs endpoint)
        try {
            const dashboard = await fetchDashboard();
            window.state.dashboard = dashboard;
            // Render KPIs with max_score from dashboard
            renderKPIs(kpis);
        } catch (dashboardError) {
            // If dashboard fails, still render KPIs without max_score
            warn('Dashboard load error (non-critical):', dashboardError);
            renderKPIs(kpis);
        }
    } catch (error) {
        logError('KPIs load error:', error);
        // Fallback to legacy dashboard endpoint
        try {
            const dashboard = await fetchDashboard();
            window.state.dashboard = dashboard;
            renderStats(dashboard);
        } catch (fallbackError) {
            logError('Dashboard fallback error:', fallbackError);
        }
    }
}

/**
 * Load dashboard statistics (legacy - kept for backward compatibility)
 */
async function loadDashboard() {
    try {
        const dashboard = await fetchDashboard();
        window.state.dashboard = dashboard;
        renderStats(dashboard);
    } catch (error) {
        logError('Dashboard load error:', error);
    }
}

/**
 * Load leads with current filters
 * Phase 1.3: Improved loading states - table spinner, filter states
 * QA: Prevent duplicate requests for same page/filters
 */
async function loadLeads() {
    // Prevent duplicate requests - check if same request is already in progress
    const currentRequest = {
        filters: JSON.stringify(window.state.filters),
        timestamp: Date.now()
    };
    
    // If same request was made within last 500ms, skip it
    if (window.state.lastLeadsRequest && 
        window.state.lastLeadsRequest.filters === currentRequest.filters &&
        (currentRequest.timestamp - window.state.lastLeadsRequest.timestamp) < 500) {
        log('Skipping duplicate leads request');
        return;
    }
    
    window.state.lastLeadsRequest = currentRequest;
    
    // Phase 1.3: Set table and filter loading states
    setTableLoading(true);
    setFiltersLoading(true);
    hideError();
    
    try {
        const response = await fetchLeads(window.state.filters);
        window.state.leads = response.leads;
        window.state.pagination = {
            total: response.total,
            page: response.page,
            page_size: response.page_size,
            total_pages: response.total_pages
        };
        
        // Clear breakdown cache when leads are refreshed (data might have changed)
        // Note: We keep cache for better UX, but could clear it if needed
        // window.state.breakdownCache = {};
        
        renderLeadsTable(response.leads);
        renderPagination();  // G19: Render pagination UI
        updateSortIcons();  // G19: Update sort icons
        bindSortableHeaders();  // G19: Re-bind sortable headers (in case table was re-rendered)
        
        // Update KPIs after leads load
        await loadKPIs();  // G19: Use new KPIs endpoint
    } catch (error) {
        showError(`Lead yükleme hatası: ${error.message}`);
        logError('Leads load error:', error);
    } finally {
        // Phase 1.3: Hide table and filter loading states
        setTableLoading(false);
        setFiltersLoading(false);
    }
}

/**
 * Apply filters from UI
 * Phase 1.4: Save filter state to localStorage
 */
function applyFilters() {
    const segment = document.getElementById('filter-segment').value;
    const minScore = document.getElementById('filter-min-score').value;
    const provider = document.getElementById('filter-provider').value;
    
    // G19: Preserve search, sorting, and pagination when applying filters
    window.state.filters.segment = segment || '';
    window.state.filters.minScore = minScore ? parseInt(minScore, 10) : null;
    window.state.filters.provider = provider || '';
    window.state.filters.page = 1; // Reset to first page on filter change
    
    // Phase 1.4: Save filter state to localStorage
    saveFilterState();
    
    loadLeads();
}

/**
 * Clear all filters (Phase 1.4)
 */
function clearFilters() {
    document.getElementById('filter-segment').value = '';
    document.getElementById('filter-provider').value = '';
    document.getElementById('filter-min-score').value = '';
    document.getElementById('filter-search').value = '';
    
    // Reset state filters
    window.state.filters.segment = '';
    window.state.filters.provider = '';
    window.state.filters.minScore = null;
    window.state.filters.search = '';
    window.state.filters.page = 1;
    
    // Phase 1.4: Save cleared state to localStorage
    saveFilterState();
    
    // Reload leads with default filters
    loadLeads();
}

/**
 * Get current filter state from UI (Phase 1.4)
 */
function getCurrentFilterState() {
    return {
        segment: document.getElementById('filter-segment')?.value || '',
        provider: document.getElementById('filter-provider')?.value || '',
        minScore: document.getElementById('filter-min-score')?.value || '',
        search: document.getElementById('filter-search')?.value || ''
    };
}

/**
 * Save filter state to localStorage (Phase 1.4)
 */
function saveFilterState() {
    const state = getCurrentFilterState();
    try {
        localStorage.setItem('hunter:mini-ui:filters', JSON.stringify(state));
    } catch (error) {
        // localStorage not available or quota exceeded
        warn('Failed to save filter state:', error);
    }
}

/**
 * Restore filter state from localStorage (Phase 1.4)
 */
function restoreFilterState() {
    try {
        const raw = localStorage.getItem('hunter:mini-ui:filters');
        if (!raw) return;
        
        const state = JSON.parse(raw);
        
        if (state.segment !== undefined) {
            const segmentEl = document.getElementById('filter-segment');
            if (segmentEl) segmentEl.value = state.segment;
        }
        if (state.provider !== undefined) {
            const providerEl = document.getElementById('filter-provider');
            if (providerEl) providerEl.value = state.provider;
        }
        if (state.minScore !== undefined) {
            const minScoreEl = document.getElementById('filter-min-score');
            if (minScoreEl) minScoreEl.value = state.minScore;
        }
        if (state.search !== undefined) {
            const searchEl = document.getElementById('filter-search');
            if (searchEl) searchEl.value = state.search;
        }
        
        // Update window.state.filters to match restored UI state
        window.state.filters.segment = state.segment || '';
        window.state.filters.provider = state.provider || '';
        window.state.filters.minScore = state.minScore ? parseInt(state.minScore, 10) : null;
        window.state.filters.search = state.search || '';
    } catch (error) {
        warn('Failed to restore filter state:', error);
    }
}

/**
 * Refresh leads (callback for forms)
 */
function refreshLeads() {
    loadLeads();
}

/**
 * Handle CSV/Excel export (Gün 3)
 */
/**
 * Handle export (CSV/Excel)
 * Phase 1.3: Improved loading state with setExportLoading
 */
async function handleExport(format = 'csv') {
    // Phase 1.3: Set export loading state
    setExportLoading(true);
    
    try {
        const { exportLeads } = await import('./api.js');
        await exportLeads(window.state.filters, format);
        showToast(`Export başarılı! ${format.toUpperCase()} dosyası indirildi.`, 'success');
    } catch (error) {
        showToast(`Export hatası: ${error.message}`, 'error');
    } finally {
        // Phase 1.3: Hide export loading state
        setExportLoading(false);
    }
}

/**
 * Phase 1.5: Enhanced toast notification with icons, better animations, and stacking
 */
function showToast(message, type = 'info', duration = 4000) {
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    
    // Phase 1.5: Add icon based on type
    const icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    
    const icon = icons[type] || icons['info'];
    
    // Phase 1.5: Structure with icon and message
    toast.innerHTML = `
        <span class="toast__icon">${icon}</span>
        <span class="toast__message">${escapeHtml(message)}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Phase 1.5: Update toast positions for stacking
    updateToastPositions();
    
    // Phase 1.5: Auto-dismiss with smooth animation
    const dismissTimeout = setTimeout(() => {
        dismissToast(toast);
    }, duration);
    
    // Phase 1.5: Allow manual dismiss on click
    toast.addEventListener('click', () => {
        clearTimeout(dismissTimeout);
        dismissToast(toast);
    });
    
    // Phase 1.5: Add hover to pause auto-dismiss
    let pauseTimeout;
    toast.addEventListener('mouseenter', () => {
        clearTimeout(dismissTimeout);
    });
    
    toast.addEventListener('mouseleave', () => {
        pauseTimeout = setTimeout(() => {
            dismissToast(toast);
        }, duration);
    });
}

/**
 * Phase 1.5: Dismiss toast with animation
 */
function dismissToast(toast) {
    toast.classList.add('toast--dismissing');
    setTimeout(() => {
        if (toast.parentNode) {
            document.body.removeChild(toast);
            updateToastPositions();
        }
    }, 300);
}

/**
 * Phase 1.5: Update toast positions for stacking
 */
function updateToastPositions() {
    const toasts = document.querySelectorAll('.toast:not(.toast--dismissing)');
    toasts.forEach((toast, index) => {
        toast.style.top = `${1 + (index * 5.5)}rem`;
    });
}

/**
 * Phase 1.5: Escape HTML helper
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * G19: Render pagination UI
 */
function renderPagination() {
    const paginationEl = document.getElementById('pagination');
    const paginationInfo = document.getElementById('pagination-info');
    const paginationPages = document.getElementById('pagination-pages');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    
    if (!paginationEl || !paginationInfo || !paginationPages || !btnPrev || !btnNext) {
        return; // Elements not found, skip rendering
    }
    
    const { total, page, page_size, total_pages } = window.state.pagination;
    
    // Hide pagination if no results or only one page
    if (total === 0 || total_pages <= 1) {
        paginationEl.style.display = 'none';
        return;
    }
    
    paginationEl.style.display = 'flex';
    
    // Update info text with page numbers
    const start = (page - 1) * page_size + 1;
    const end = Math.min(page * page_size, total);
    paginationInfo.innerHTML = `<span class="pagination__page-info">Sayfa <strong>${page}</strong> / ${total_pages}</span> <span class="pagination__text">(${start}-${end} / ${total})</span>`;
    
    // Update prev/next buttons
    btnPrev.disabled = page <= 1;
    btnNext.disabled = page >= total_pages;
    
    // Render page numbers
    paginationPages.innerHTML = '';
    
    // Show first page
    if (total_pages > 0) {
        const firstPage = createPageButton(1);
        paginationPages.appendChild(firstPage);
    }
    
    // Show ellipsis if needed
    if (page > 3 && total_pages > 5) {
        const ellipsis = document.createElement('span');
        ellipsis.className = 'pagination__page pagination__page--ellipsis';
        ellipsis.textContent = '...';
        paginationPages.appendChild(ellipsis);
    }
    
    // Show pages around current page
    const startPage = Math.max(2, page - 1);
    const endPage = Math.min(total_pages - 1, page + 1);
    
    for (let i = startPage; i <= endPage; i++) {
        if (i !== 1 && i !== total_pages) {
            paginationPages.appendChild(createPageButton(i));
        }
    }
    
    // Show ellipsis if needed
    if (page < total_pages - 2 && total_pages > 5) {
        const ellipsis = document.createElement('span');
        ellipsis.className = 'pagination__page pagination__page--ellipsis';
        ellipsis.textContent = '...';
        paginationPages.appendChild(ellipsis);
    }
    
    // Show last page
    if (total_pages > 1) {
        paginationPages.appendChild(createPageButton(total_pages));
    }
}

/**
 * G19: Create page number button
 */
function createPageButton(pageNum) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'pagination__page';
    if (pageNum === window.state.pagination.page) {
        button.classList.add('pagination__page--active');
    }
    button.textContent = pageNum;
    button.addEventListener('click', () => {
        window.state.filters.page = pageNum;
        loadLeads();
    });
    return button;
}

/**
 * G19: Bind sortable table headers
 */
function bindSortableHeaders() {
    const sortableHeaders = document.querySelectorAll('.leads-table__cell--sortable');
    sortableHeaders.forEach(header => {
        // Remove existing listeners to avoid duplicates
        const newHeader = header.cloneNode(true);
        header.parentNode.replaceChild(newHeader, header);
        
        newHeader.addEventListener('click', () => {
            const sortBy = newHeader.getAttribute('data-sort');
            if (!sortBy) return;
            
            // Toggle sort order if same field, otherwise set to asc
            if (window.state.filters.sortBy === sortBy) {
                window.state.filters.sortOrder = window.state.filters.sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                window.state.filters.sortBy = sortBy;
                window.state.filters.sortOrder = 'asc';
            }
            
            // Reset to first page on sort change
            window.state.filters.page = 1;
            
            loadLeads();
        });
    });
}

/**
 * G19: Update sort icons in table headers
 */
function updateSortIcons() {
    const sortableHeaders = document.querySelectorAll('.leads-table__cell--sortable');
    sortableHeaders.forEach(header => {
        const sortBy = header.getAttribute('data-sort');
        header.classList.remove('sort-asc', 'sort-desc');
        
        if (window.state.filters.sortBy === sortBy) {
            if (window.state.filters.sortOrder === 'asc') {
                header.classList.add('sort-asc');
            } else {
                header.classList.add('sort-desc');
            }
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

