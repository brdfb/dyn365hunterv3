// API Client - All fetch calls
// Can be overridden by deployment (e.g., nginx template sets window.HUNTER_API_BASE_URL)
import { log, error as logError } from './logger.js';

const API_BASE_URL = window.HUNTER_API_BASE_URL || 'http://localhost:8000';

/**
 * Get user-friendly error message from API response
 */
async function getErrorMessage(response) {
    try {
        const errorData = await response.json();
        // Try to extract user-friendly message
        if (errorData.detail) {
            return errorData.detail;
        }
        if (errorData.message) {
            return errorData.message;
        }
        if (errorData.error) {
            return errorData.error;
        }
    } catch (e) {
        // JSON parse failed, use status text
    }
    
    // Fallback to status-based messages
    switch (response.status) {
        case 400:
            return 'Geçersiz istek. Lütfen girdiğiniz bilgileri kontrol edin.';
        case 401:
            return 'Yetkilendirme hatası. Lütfen tekrar giriş yapın.';
        case 403:
            return 'Bu işlem için yetkiniz bulunmuyor.';
        case 404:
            return 'İstenen kaynak bulunamadı.';
        case 409:
            return 'Bu kayıt zaten mevcut.';
        case 422:
            return 'Girilen veriler geçersiz. Lütfen kontrol edin.';
        case 429:
            return 'Çok fazla istek gönderildi. Lütfen bir süre bekleyin.';
        case 500:
            return 'Sunucu hatası. Lütfen daha sonra tekrar deneyin.';
        case 503:
            return 'Servis şu anda kullanılamıyor. Lütfen daha sonra tekrar deneyin.';
        default:
            return `Sunucu hatası (${response.status}). Lütfen daha sonra tekrar deneyin.`;
    }
}

/**
 * Fetch leads with filters (G19: Updated for paginated response)
 * Returns: { leads: [], total: 0, page: 1, page_size: 50, total_pages: 0 }
 */
export async function fetchLeads(filters = {}) {
    const params = new URLSearchParams();
    if (filters.segment) params.append('segment', filters.segment);
    if (filters.minScore !== null && filters.minScore !== undefined) {
        params.append('min_score', filters.minScore);
    }
    if (filters.provider) params.append('provider', filters.provider);
    if (filters.referralType) params.append('referral_type', filters.referralType);
    
    // G19: Add pagination and sorting parameters
    if (filters.page) params.append('page', filters.page);
    if (filters.pageSize) params.append('page_size', filters.pageSize);
    if (filters.sortBy) params.append('sort_by', filters.sortBy);
    if (filters.sortOrder) params.append('sort_order', filters.sortOrder);
    if (filters.search) params.append('search', filters.search);

    const url = `${API_BASE_URL}/leads${params.toString() ? '?' + params.toString() : ''}`;
    log('Fetching leads:', url);
    const response = await fetch(url);
    
    if (!response.ok) {
        const errorMessage = await getErrorMessage(response);
        logError('Failed to fetch leads:', errorMessage);
        throw new Error(errorMessage);
    }
    
    const data = await response.json();
    
    // G19: Handle new paginated response format
    // Backward compatibility: if response is array, wrap it
    if (Array.isArray(data)) {
        // Old format (backward compatibility)
        return {
            leads: data,
            total: data.length,
            page: 1,
            page_size: data.length,
            total_pages: 1
        };
    } else if (data.leads && Array.isArray(data.leads)) {
        // New format: return full pagination metadata
        return {
            leads: data.leads,
            total: data.total || 0,
            page: data.page || 1,
            page_size: data.page_size || 50,
            total_pages: data.total_pages || 1
        };
    } else {
        // Unexpected format, return as-is
        return {
            leads: [],
            total: 0,
            page: 1,
            page_size: 50,
            total_pages: 0
        };
    }
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
        const errorMessage = await getErrorMessage(response);
        logError('Ingest domain failed:', errorMessage);
        throw new Error(errorMessage);
    }

    return await response.json();
}

/**
 * Sync Partner Center referrals
 */
export async function syncPartnerCenterReferrals() {
    const response = await fetch(`${API_BASE_URL}/api/referrals/sync`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    });

    if (!response.ok) {
        const errorMessage = await getErrorMessage(response);
        logError('Partner Center sync failed:', errorMessage);
        throw new Error(errorMessage);
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
        const errorMessage = await getErrorMessage(response);
        logError('Scan domain failed:', errorMessage);
        throw new Error(errorMessage);
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
        const errorMessage = await getErrorMessage(response);
        logError('Upload CSV failed:', errorMessage);
        throw new Error(errorMessage);
    }

    return await response.json();
}

/**
 * Get job progress
 */
export async function getJobProgress(jobId) {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
    
    if (!response.ok) {
        const errorMessage = await getErrorMessage(response);
        logError('Get job progress failed:', errorMessage);
        throw new Error(errorMessage);
    }
    
    return await response.json();
}

/**
 * Export leads to CSV or Excel (Gün 3)
 */
export async function exportLeads(filters = {}, format = 'csv') {
    const params = new URLSearchParams();
    if (filters.segment) params.append('segment', filters.segment);
    if (filters.minScore !== null && filters.minScore !== undefined) {
        params.append('min_score', filters.minScore);
    }
    if (filters.provider) params.append('provider', filters.provider);
    if (filters.search) params.append('search', filters.search);
    // v1.1: Convert 'excel' to 'xlsx' for API compatibility
    const apiFormat = format === 'excel' ? 'xlsx' : format;
    params.append('format', apiFormat);

    const url = `${API_BASE_URL}/leads/export${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);

    if (!response.ok) {
        const errorMessage = await getErrorMessage(response);
        logError('Export leads failed:', errorMessage);
        throw new Error(errorMessage);
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    
    // Get filename from Content-Disposition header or use default
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = format === 'excel' ? 'leads.xlsx' : 'leads.csv';
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
 * Export PDF for a domain (Gün 3)
 */
export async function exportPDF(domain) {
    const url = `${API_BASE_URL}/leads/${encodeURIComponent(domain)}/summary.pdf`;
    window.open(url, '_blank');
}

/**
 * Fetch dashboard statistics (legacy endpoint - kept for backward compatibility)
 */
export async function fetchDashboard() {
    const response = await fetch(`${API_BASE_URL}/dashboard`);
    
    if (!response.ok) {
        const errorMessage = await getErrorMessage(response);
        logError('Fetch dashboard failed:', errorMessage);
        throw new Error(errorMessage);
    }
    
    return await response.json();
}

/**
 * Fetch dashboard KPIs (G19 - New endpoint)
 */
export async function fetchKPIs() {
    const response = await fetch(`${API_BASE_URL}/dashboard/kpis`);
    
    if (!response.ok) {
        const errorMessage = await getErrorMessage(response);
        logError('Fetch KPIs failed:', errorMessage);
        throw new Error(errorMessage);
    }
    
    return await response.json();
}

/**
 * Fetch score breakdown for a domain (G19)
 */
export async function fetchScoreBreakdown(domain) {
    const response = await fetch(`${API_BASE_URL}/leads/${encodeURIComponent(domain)}/score-breakdown`);
    
    if (!response.ok) {
        const errorMessage = await getErrorMessage(response);
        logError('Fetch score breakdown failed:', errorMessage);
        throw new Error(errorMessage);
    }
    
    return await response.json();
}

/**
 * Fetch sales summary for a domain (G21 Phase 2)
 */
export async function fetchSalesSummary(domain) {
    const response = await fetch(`${API_BASE_URL}/api/v1/leads/${encodeURIComponent(domain)}/sales-summary`);
    
    if (!response.ok) {
        const errorMessage = await getErrorMessage(response);
        logError('Fetch sales summary failed:', errorMessage);
        throw new Error(errorMessage);
    }
    
    return await response.json();
}

/**
 * Fetch referral inbox with filters (Phase 2)
 * Returns: { referrals: [], total: 0, page: 1, page_size: 50 }
 */
export async function fetchReferralInbox(filters = {}) {
    const params = new URLSearchParams();
    if (filters.linkStatus) params.append('link_status', filters.linkStatus);
    if (filters.referralType) params.append('referral_type', filters.referralType);
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);
    if (filters.page) params.append('page', filters.page);
    if (filters.pageSize) params.append('page_size', filters.pageSize);

    const url = `${API_BASE_URL}/api/v1/partner-center/referrals/inbox${params.toString() ? '?' + params.toString() : ''}`;
    log('Fetching referral inbox:', url);
    const response = await fetch(url);
    
    if (!response.ok) {
        const errorMessage = await getErrorMessage(response);
        logError('Failed to fetch referral inbox:', errorMessage);
        throw new Error(errorMessage);
    }
    
    return await response.json();
}

/**
 * Link referral to existing lead (Phase 2)
 */
export async function linkReferralToLead(referralId, leadDomain) {
    const response = await fetch(`${API_BASE_URL}/api/v1/partner-center/referrals/${encodeURIComponent(referralId)}/link`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ lead_domain: leadDomain }),
    });

    if (!response.ok) {
        const errorMessage = await getErrorMessage(response);
        logError('Link referral failed:', errorMessage);
        throw new Error(errorMessage);
    }

    return await response.json();
}

/**
 * Create lead from referral (Phase 2)
 */
export async function createLeadFromReferral(referralId, companyNameOverride = null, notes = null) {
    const body = {};
    if (companyNameOverride) body.company_name_override = companyNameOverride;
    if (notes) body.notes = notes;

    const response = await fetch(`${API_BASE_URL}/api/v1/partner-center/referrals/${encodeURIComponent(referralId)}/create-lead`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const errorMessage = await getErrorMessage(response);
        logError('Create lead from referral failed:', errorMessage);
        throw new Error(errorMessage);
    }

    return await response.json();
}

