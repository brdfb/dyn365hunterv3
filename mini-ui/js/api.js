// API Client - All fetch calls
const API_BASE_URL = 'http://localhost:8000';

/**
 * Fetch leads with filters
 */
export async function fetchLeads(filters = {}) {
    const params = new URLSearchParams();
    if (filters.segment) params.append('segment', filters.segment);
    if (filters.minScore !== null && filters.minScore !== undefined) {
        params.append('min_score', filters.minScore);
    }
    if (filters.provider) params.append('provider', filters.provider);

    const url = `${API_BASE_URL}/leads${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

/**
 * Ingest a single domain (required before scan)
 */
export async function ingestDomain(domain, companyName = null) {
    const body = { domain };
    if (companyName) {
        body.company_name = companyName;
    }

    const response = await fetch(`${API_BASE_URL}/ingest/domain`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

/**
 * Scan a single domain (domain must be ingested first)
 */
export async function scanDomain(domain) {
    const body = { domain };

    const response = await fetch(`${API_BASE_URL}/scan/domain`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

/**
 * Upload CSV/Excel file
 */
export async function uploadCsv(file, autoDetect = false) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Always enable auto_scan to create leads automatically
    const params = new URLSearchParams();
    if (autoDetect) {
        params.append('auto_detect_columns', 'true');
    }
    params.append('auto_scan', 'true');  // Enable automatic scanning
    
    const url = `${API_BASE_URL}/ingest/csv${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

/**
 * Get job progress
 */
export async function getJobProgress(jobId) {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

/**
 * Export leads to CSV
 */
export async function exportLeads(filters = {}) {
    const params = new URLSearchParams();
    if (filters.segment) params.append('segment', filters.segment);
    if (filters.minScore !== null && filters.minScore !== undefined) {
        params.append('min_score', filters.minScore);
    }
    if (filters.provider) params.append('provider', filters.provider);
    params.append('format', 'csv');

    const url = `${API_BASE_URL}/leads/export${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    
    // Get filename from Content-Disposition header or use default
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = 'leads.csv';
    if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (filenameMatch) {
            filename = filenameMatch[1];
        }
    }
    
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(downloadUrl);
}

/**
 * Fetch dashboard statistics
 */
export async function fetchDashboard() {
    const response = await fetch(`${API_BASE_URL}/dashboard`);
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

