// UI Forms - Form binding and behavior

import { uploadCsv, scanDomain, ingestDomain, getJobProgress } from './api.js';
import { error as logError } from './logger.js';

/**
 * Bind CSV upload form
 */
export function bindCsvUploadForm(onSuccess) {
    const form = document.getElementById('form-csv-upload');
    const messageEl = document.getElementById('csv-upload-message');
    
    if (!form) {
        logError('CSV upload form not found');
        return;
    }
    
    if (!messageEl) {
        logError('CSV upload message element not found');
        return;
    }
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fileInput = document.getElementById('csv-file');
        if (!fileInput) {
            showMessage(messageEl, 'Dosya input elementi bulunamadı', 'error');
            return;
        }
        
        const autoDetectEl = document.getElementById('auto-detect');
        const autoDetect = autoDetectEl ? autoDetectEl.checked : false;
        const file = fileInput.files[0];
        
        if (!file) {
            showMessage(messageEl, 'Lütfen bir dosya seçin', 'error');
            return;
        }
        
        const button = form.querySelector('button[type="submit"]');
        if (!button) {
            showMessage(messageEl, 'Submit butonu bulunamadı', 'error');
            return;
        }
        const originalButtonText = button.textContent;
        button.disabled = true;
        button.textContent = 'Yükleniyor...';
        
        // Create progress container
        const progressContainer = document.createElement('div');
        progressContainer.id = 'csv-progress-container';
        progressContainer.className = 'progress-container';
        progressContainer.innerHTML = `
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
            </div>
            <div class="progress-info" id="progress-info">Yükleniyor...</div>
            <div class="progress-stats" id="progress-stats"></div>
        `;
        messageEl.parentNode.insertBefore(progressContainer, messageEl);
        messageEl.style.display = 'none';
        
        try {
            const result = await uploadCsv(file, autoDetect);
            const jobId = result.job_id;
            
            if (jobId) {
                // Poll for progress
                const pollInterval = setInterval(async () => {
                    try {
                        const progress = await getJobProgress(jobId);
                        
                        // Update progress bar
                        const progressFill = document.getElementById('progress-fill');
                        const progressInfo = document.getElementById('progress-info');
                        const progressStats = document.getElementById('progress-stats');
                        
                        if (progressFill && progressInfo && progressStats) {
                            progressFill.style.width = `${progress.progress_percent}%`;
                            progressInfo.textContent = progress.message || 'İşleniyor...';
                            progressStats.innerHTML = `
                                <span>İşlenen: ${progress.processed}/${progress.total}</span>
                                <span>Başarılı: ${progress.successful}</span>
                                <span>Başarısız: ${progress.failed}</span>
                                <span>Kalan: ${progress.remaining}</span>
                                <span>İlerleme: ${progress.progress_percent.toFixed(1)}%</span>
                            `;
                        }
                        
                        // Check if completed
                        if (progress.status === 'completed' || progress.status === 'failed') {
                            clearInterval(pollInterval);
                            progressContainer.remove();
                            
                            if (progress.status === 'completed') {
                                // progress.successful is the number of scanned domains (leads)
                                const leadCount = progress.successful || 0;
                                showMessage(messageEl, `Başarılı! ${leadCount} domain scan edildi ve lead listesine eklendi.`, 'success');
                            } else {
                                showMessage(messageEl, `Hata: İşlem başarısız oldu.`, 'error');
                            }
                            
                            fileInput.value = '';
                            button.disabled = false;
                            button.textContent = originalButtonText;
                            
                            // Auto-refresh leads if callback provided
                            if (onSuccess) {
                                setTimeout(() => onSuccess(), 1000);
                            }
                        }
                    } catch (error) {
                        logError('Progress polling error:', error);
                    }
                }, 1000); // Poll every 1 second
            } else {
                // Fallback to old behavior if no job_id
                const scanned = result.scanned || 0;
                const ingested = result.ingested || 0;
                
                progressContainer.remove();
                
                if (scanned > 0) {
                    showMessage(messageEl, `Başarılı! ${ingested} domain eklendi, ${scanned} domain scan edildi ve lead listesine eklendi.`, 'success');
                } else {
                    showMessage(messageEl, `Başarılı! ${ingested} domain eklendi. (Not: Domain'ler scan edilmedi, lead listesinde görünmeyecek.)`, 'success');
                }
                fileInput.value = '';
                button.disabled = false;
                button.textContent = originalButtonText;
                
                if (onSuccess) {
                    setTimeout(() => onSuccess(), 1000);
                }
            }
        } catch (error) {
            const progressContainer = document.getElementById('csv-progress-container');
            if (progressContainer) {
                progressContainer.remove();
            }
            showMessage(messageEl, `Hata: ${error.message}`, 'error');
            button.disabled = false;
            button.textContent = originalButtonText;
        }
    });
}

/**
 * Bind domain scan form
 */
export function bindScanDomainForm(onSuccess) {
    const form = document.getElementById('form-domain-scan');
    const messageEl = document.getElementById('scan-message');
    const resultEl = document.getElementById('scan-result');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const domainInput = document.getElementById('domain-input');
        const companyInput = document.getElementById('company-name');
        const domain = domainInput.value.trim();
        const companyName = companyInput.value.trim() || null;
        
        if (!domain) {
            showMessage(messageEl, 'Lütfen bir domain girin', 'error');
            return;
        }
        
        const button = form.querySelector('button[type="submit"]');
        const originalButtonText = button.textContent;
        button.disabled = true;
        button.textContent = 'Yükleniyor...';
        showMessage(messageEl, 'Taranıyor...', 'info');
        resultEl.classList.remove('scan-result--visible');
        
        try {
            // First, ingest domain if company name is provided or if domain doesn't exist
            try {
                await ingestDomain(domain, companyName);
                showMessage(messageEl, 'Domain eklendi, taranıyor...', 'info');
            } catch (ingestError) {
                // If ingest fails with 400, domain might already exist - continue to scan
                if (!ingestError.message.includes('already exists')) {
                    throw ingestError;
                }
            }
            
            // Then scan the domain
            const result = await scanDomain(domain);
            
            // Show result
            resultEl.innerHTML = `
                <div class="scan-result__item">
                    <span class="scan-result__label">Domain:</span>
                    <span class="scan-result__value">${escapeHtml(result.domain)}</span>
                </div>
                <div class="scan-result__item">
                    <span class="scan-result__label">Skor:</span>
                    <span class="scan-result__value">${result.score || '-'}</span>
                </div>
                <div class="scan-result__item">
                    <span class="scan-result__label">Segment:</span>
                    <span class="scan-result__value">${escapeHtml(result.segment || '-')}</span>
                </div>
                <div class="scan-result__item">
                    <span class="scan-result__label">Provider:</span>
                    <span class="scan-result__value">${escapeHtml(result.provider || '-')}</span>
                </div>
            `;
            resultEl.classList.add('scan-result--visible');
            showMessage(messageEl, 'Tarama tamamlandı!', 'success');
            
            // Auto-refresh leads if callback provided
            if (onSuccess) {
                setTimeout(() => onSuccess(), 1000);
            }
        } catch (error) {
            showMessage(messageEl, `Hata: ${error.message}`, 'error');
            resultEl.classList.remove('scan-result--visible');
        } finally {
            button.disabled = false;
            button.textContent = originalButtonText;
        }
    });
}

/**
 * Show message in form message area
 */
function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `form__message form__message--${type}`;
    element.style.display = 'block';
    
    if (type === 'info') {
        element.style.backgroundColor = '#d1ecf1';
        element.style.color = '#0c5460';
        element.style.border = '1px solid #bee5eb';
    } else if (type === 'success') {
        element.style.backgroundColor = '#d4edda';
        element.style.color = '#155724';
        element.style.border = '1px solid #c3e6cb';
    } else if (type === 'error') {
        element.style.backgroundColor = '#f8d7da';
        element.style.color = '#721c24';
        element.style.border = '1px solid #f5c6cb';
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

