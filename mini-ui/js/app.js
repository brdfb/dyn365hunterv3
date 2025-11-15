// App - Global state, initialization, orchestration

import { fetchLeads, fetchDashboard, exportLeads } from './api.js';
import { renderLeadsTable, renderStats, showLoading, hideLoading, showError, hideError } from './ui-leads.js';
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
    
    // Bind export button
    document.getElementById('btn-export').addEventListener('click', handleExport);
    
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
    
    // Load initial data
    await loadDashboard();
    await loadLeads();
}

/**
 * Load dashboard statistics
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
        
        // Update dashboard after leads load
        await loadDashboard();
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
 * Handle CSV export
 */
async function handleExport() {
    const button = document.getElementById('btn-export');
    const originalText = button.textContent;
    
    button.disabled = true;
    button.textContent = 'Export ediliyor...';
    
    try {
        await exportLeads(window.state.filters);
        button.textContent = 'Export başarılı!';
        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);
    } catch (error) {
        showError(`Export hatası: ${error.message}`);
        button.textContent = originalText;
    } finally {
        button.disabled = false;
    }
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
    
    // Update info text
    const start = (page - 1) * page_size + 1;
    const end = Math.min(page * page_size, total);
    paginationInfo.textContent = `${start}-${end} / ${total}`;
    
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

