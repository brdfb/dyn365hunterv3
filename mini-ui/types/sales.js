/**
 * Sales Summary API - JSDoc Type Definitions (JavaScript)
 * 
 * This file contains JSDoc type definitions for JavaScript projects.
 * Use these types in JSDoc comments for better IDE support.
 * 
 * API Contract: docs/api/SALES-SUMMARY-V1-CONTRACT.md
 * Version: 1.0.0
 * Date: 2025-01-28
 */

/**
 * @typedef {Object} SalesSummary
 * @property {string} domain - Domain name (normalized)
 * @property {string} one_liner - One-sentence sales summary (Turkish)
 * @property {string[]} call_script - Call script bullets for sales outreach (Turkish)
 * @property {string[]} discovery_questions - Discovery questions for sales qualification (Turkish)
 * @property {OfferTier} offer_tier - Offer tier recommendation
 * @property {number} opportunity_potential - Opportunity potential score (0-100)
 * @property {'low'|'medium'|'high'} urgency - Urgency level
 * @property {SalesSummaryMetadata} metadata - Additional metadata
 */

/**
 * @typedef {Object} OfferTier
 * @property {'Business Basic'|'Business Standard'|'Enterprise'} tier - Tier name
 * @property {string} license - License type (same as tier)
 * @property {number} price_per_user_per_month - Price per user per month in EUR
 * @property {number|null} migration_fee - One-time migration fee in EUR (null if not applicable)
 * @property {number|null} defender_price_per_user_per_month - Defender price per user per month in EUR (null if not applicable)
 * @property {number|null} consulting_fee - One-time consulting fee in EUR (null if not applicable)
 * @property {string} recommendation - Human-readable recommendation (Turkish)
 */

/**
 * @typedef {Object} SalesSummaryMetadata
 * @property {string} domain - Domain name
 * @property {'M365'|'Google'|'Local'|'Yandex'|'Unknown'|null} provider - Provider name
 * @property {'Migration'|'Existing'|'Cold'|'Skip'|null} segment - Lead segment
 * @property {number|null} readiness_score - Readiness score (0-100)
 * @property {number|null} priority_score - Priority score (1-7, 1 is highest)
 * @property {'small'|'medium'|'large'|null} tenant_size - Tenant size
 * @property {string|null} local_provider - Local provider name (e.g., "TürkHost", "Natro")
 * @property {string} generated_at - ISO 8601 timestamp when summary was generated
 */

/**
 * Opportunity potential score interpretation ranges:
 * - 70-100: High priority, immediate action
 * - 50-69: Medium priority, follow up within 1 week
 * - 30-49: Low priority, long-term nurture
 * - 0-29: Very low priority, quarterly check
 * 
 * @param {number} score - Opportunity potential score (0-100)
 * @returns {'high'|'medium'|'low'|'very_low'} Range category
 */
function interpretOpportunityPotential(score) {
  if (score >= 70) return 'high';
  if (score >= 50) return 'medium';
  if (score >= 30) return 'low';
  return 'very_low';
}

/**
 * Get opportunity potential badge color
 * 
 * @param {number} score - Opportunity potential score (0-100)
 * @returns {string} CSS color class or hex color
 */
function getOpportunityBadgeColor(score) {
  if (score >= 70) return '#22c55e'; // green
  if (score >= 50) return '#eab308'; // yellow
  if (score >= 30) return '#f97316'; // orange
  return '#ef4444'; // red
}

/**
 * Get urgency badge color
 * 
 * @param {'low'|'medium'|'high'} urgency - Urgency level
 * @returns {string} CSS color class or hex color
 */
function getUrgencyBadgeColor(urgency) {
  switch (urgency) {
    case 'high': return '#ef4444'; // red
    case 'medium': return '#f97316'; // orange
    case 'low': return '#6b7280'; // gray
  }
}

/**
 * Fetch sales summary from API
 * 
 * @param {string} domain - Domain name
 * @returns {Promise<SalesSummary>} Sales summary response
 * @throws {Error} If API request fails
 * 
 * @example
 * ```javascript
 * const summary = await fetchSalesSummary('example.com');
 * console.log(summary.one_liner);
 * ```
 */
async function fetchSalesSummary(domain) {
  const response = await fetch(`/api/v1/leads/${domain}/sales-summary`);
  if (!response.ok) {
    throw new Error(`Failed to fetch sales summary: ${response.statusText}`);
  }
  return response.json();
}

