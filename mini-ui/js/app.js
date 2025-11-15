// App - Global state, initialization, orchestration

import { fetchLeads, fetchKPIs, fetchDashboard, fetchScoreBreakdown } from './api.js';
import { renderLeadsTable, renderStats, renderKPIs, showLoading, hideLoading, showError, hideError, showScoreBreakdown, hideScoreBreakdown, showScoreBreakdownError } from './ui-leads.js';
import { bindCsvUploadForm, bindScanDomainForm } from './ui-forms.js';

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
    loading: false
};

/**
 * Initialize application
 */
async function init() {
    // Bind forms
    bindCsvUploadForm(refreshLeads);
    bindScanDomainForm(refreshLeads);
    
    // Bind filter button
    document.getElementById('btn-filter').addEventListener('click', applyFilters);
    
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
    const searchInput = document.getElementById('filter-search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                window.state.filters.search = e.target.value.trim();
                window.state.filters.page = 1; // Reset to first page on search
                loadLeads();
            }, 500); // 500ms debounce
        });
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
                showLoading();
                try {
                    const breakdown = await fetchScoreBreakdown(domain);
                    showScoreBreakdown(breakdown, domain);
                } catch (error) {
                    // Check if domain is not scanned
                    if (error.message.includes('henüz taranmamış') || error.message.includes('has not been scanned')) {
                        showScoreBreakdownError(domain, error.message);
                    } else {
                        showError(`Skor detayı yüklenemedi: ${error.message}`);
                    }
                } finally {
                    hideLoading();
                }
            }
        }
    });
    
    // Listen for refresh events
    window.addEventListener('refreshLeads', () => {
        setTimeout(() => loadLeads(), 1000);
    });
    
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
            console.warn('Dashboard load error (non-critical):', dashboardError);
            renderKPIs(kpis);
        }
    } catch (error) {
        console.error('KPIs load error:', error);
        // Fallback to legacy dashboard endpoint
        try {
            const dashboard = await fetchDashboard();
            window.state.dashboard = dashboard;
            renderStats(dashboard);
        } catch (fallbackError) {
            console.error('Dashboard fallback error:', fallbackError);
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
        console.error('Dashboard load error:', error);
    }
}

/**
 * Load leads with current filters
 */
async function loadLeads() {
    showLoading();
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
        
        renderLeadsTable(response.leads);
        renderPagination();  // G19: Render pagination UI
        updateSortIcons();  // G19: Update sort icons
        bindSortableHeaders();  // G19: Re-bind sortable headers (in case table was re-rendered)
        
        // Update KPIs after leads load
        await loadKPIs();  // G19: Use new KPIs endpoint
    } catch (error) {
        showError(`Lead yükleme hatası: ${error.message}`);
        console.error('Leads load error:', error);
    } finally {
        hideLoading();
    }
}

/**
 * Apply filters from UI
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
    
    loadLeads();
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
async function handleExport(format = 'csv') {
    const buttonId = format === 'excel' ? 'btn-export-excel' : 'btn-export-csv';
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    const originalText = button.textContent;
    
    button.disabled = true;
    button.textContent = 'Export ediliyor...';
    
    try {
        const { exportLeads } = await import('./api.js');
        await exportLeads(window.state.filters, format);
        showToast(`Export başarılı! ${format.toUpperCase()} dosyası indirildi.`, 'success');
        button.textContent = originalText;
    } catch (error) {
        showToast(`Export hatası: ${error.message}`, 'error');
        button.textContent = originalText;
    } finally {
        button.disabled = false;
    }
}

/**
 * Show toast notification (Gün 3)
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
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

