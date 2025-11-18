// Utility Functions - Shared helpers

/**
 * Escape HTML to prevent XSS
 * @param {string|null|undefined} text - Text to escape
 * @returns {string} Escaped HTML string
 */
export function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Validate domain format
 * @param {string} domain - Domain to validate
 * @returns {{valid: boolean, error?: string}} Validation result
 */
export function validateDomain(domain) {
    if (!domain || typeof domain !== 'string') {
        return { valid: false, error: 'Domain boş olamaz' };
    }
    
    const trimmedDomain = domain.trim();
    if (!trimmedDomain) {
        return { valid: false, error: 'Domain boş olamaz' };
    }
    
    // Basic domain format validation
    // Allows: example.com, sub.example.com, example.co.uk, example.com.tr
    // Rejects: example, example., .example.com, empty string
    const domainRegex = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$/;
    
    if (!domainRegex.test(trimmedDomain)) {
        return { valid: false, error: 'Geçersiz domain formatı. Örnek: example.com' };
    }
    
    return { valid: true };
}

