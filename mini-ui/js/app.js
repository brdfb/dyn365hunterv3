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
        provider: ''
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
        const leads = await fetchLeads(window.state.filters);
        window.state.leads = leads;
        renderLeadsTable(leads);
        
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
    
    window.state.filters = {
        segment: segment || '',
        minScore: minScore ? parseInt(minScore, 10) : null,
        provider: provider || ''
    };
    
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

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

