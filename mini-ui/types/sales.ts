/**
 * Sales Summary API - TypeScript Type Definitions
 * 
 * This file contains TypeScript interfaces for the Sales Summary API v1.
 * For JavaScript projects, use JSDoc comments with these types.
 * 
 * API Contract: docs/api/SALES-SUMMARY-V1-CONTRACT.md
 * Version: 1.0.0
 * Date: 2025-01-28
 */

/**
 * Sales Summary response from API
 * 
 * @example
 * ```typescript
 * const summary: SalesSummary = await fetch('/api/v1/leads/example.com/sales-summary')
 *   .then(r => r.json());
 * ```
 */
export interface SalesSummary {
  /** Domain name (normalized) */
  domain: string;
  
  /** One-sentence sales summary (Turkish) */
  one_liner: string;
  
  /** Call script bullets for sales outreach (Turkish) */
  call_script: string[];
  
  /** Discovery questions for sales qualification (Turkish) */
  discovery_questions: string[];
  
  /** Offer tier recommendation */
  offer_tier: OfferTier;
  
  /** Opportunity potential score (0-100) */
  opportunity_potential: number;
  
  /** Urgency level */
  urgency: 'low' | 'medium' | 'high';
  
  /** Additional metadata for debugging and context */
  metadata: SalesSummaryMetadata;
}

/**
 * Offer tier recommendation details
 */
export interface OfferTier {
  /** Tier name */
  tier: 'Business Basic' | 'Business Standard' | 'Enterprise';
  
  /** License type (same as tier) */
  license: string;
  
  /** Price per user per month in EUR */
  price_per_user_per_month: number;
  
  /** One-time migration fee in EUR (null if not applicable) */
  migration_fee: number | null;
  
  /** Defender price per user per month in EUR (null if not applicable) */
  defender_price_per_user_per_month: number | null;
  
  /** One-time consulting fee in EUR (null if not applicable) */
  consulting_fee: number | null;
  
  /** Human-readable recommendation (Turkish) */
  recommendation: string;
}

/**
 * Sales summary metadata
 */
export interface SalesSummaryMetadata {
  /** Domain name */
  domain: string;
  
  /** Provider name */
  provider: 'M365' | 'Google' | 'Local' | 'Yandex' | 'Unknown' | null;
  
  /** Lead segment */
  segment: 'Migration' | 'Existing' | 'Cold' | 'Skip' | null;
  
  /** Readiness score (0-100) */
  readiness_score: number | null;
  
  /** Priority score (1-7, 1 is highest) */
  priority_score: number | null;
  
  /** Tenant size */
  tenant_size: 'small' | 'medium' | 'large' | null;
  
  /** Local provider name (e.g., "TürkHost", "Natro") */
  local_provider: string | null;
  
  /** ISO 8601 timestamp when summary was generated */
  generated_at: string;
}

/**
 * Opportunity potential score interpretation
 * 
 * Use these ranges to interpret opportunity_potential values:
 * - 70-100: High priority, immediate action
 * - 50-69: Medium priority, follow up within 1 week
 * - 30-49: Low priority, long-term nurture
 * - 0-29: Very low priority, quarterly check
 */
export type OpportunityPotentialRange = 
  | 'high'      // 70-100
  | 'medium'    // 50-69
  | 'low'       // 30-49
  | 'very_low'; // 0-29

/**
 * Helper function to interpret opportunity potential score
 * 
 * @param score Opportunity potential score (0-100)
 * @returns Range category
 */
export function interpretOpportunityPotential(score: number): OpportunityPotentialRange {
  if (score >= 70) return 'high';
  if (score >= 50) return 'medium';
  if (score >= 30) return 'low';
  return 'very_low';
}

/**
 * Helper function to get opportunity potential badge color
 * 
 * @param score Opportunity potential score (0-100)
 * @returns CSS color class or hex color
 */
export function getOpportunityBadgeColor(score: number): string {
  if (score >= 70) return '#22c55e'; // green
  if (score >= 50) return '#eab308'; // yellow
  if (score >= 30) return '#f97316'; // orange
  return '#ef4444'; // red
}

/**
 * Helper function to get urgency badge color
 * 
 * @param urgency Urgency level
 * @returns CSS color class or hex color
 */
export function getUrgencyBadgeColor(urgency: 'low' | 'medium' | 'high'): string {
  switch (urgency) {
    case 'high': return '#ef4444'; // red
    case 'medium': return '#f97316'; // orange
    case 'low': return '#6b7280'; // gray
  }
}

/**
 * API fetch function example (for reference)
 * 
 * @example
 * ```typescript
 * async function fetchSalesSummary(domain: string): Promise<SalesSummary> {
 *   const response = await fetch(`/api/v1/leads/${domain}/sales-summary`);
 *   if (!response.ok) {
 *     throw new Error(`Failed to fetch sales summary: ${response.statusText}`);
 *   }
 *   return response.json();
 * }
 * ```
 */
export type SalesSummaryFetchFunction = (domain: string) => Promise<SalesSummary>;

