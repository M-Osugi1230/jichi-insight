import foodCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_food.json";
import foodEvidence from "../../../data/entities/policy/hokkaido_indicator_food_evidence_packets.json";
import tourismCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_tourism.json";
import tourismEvidence from "../../../data/entities/policy/hokkaido_indicator_tourism_evidence_packets.json";
import zeroCarbonCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_zero_carbon.json";
import zeroCarbonEvidence from "../../../data/entities/policy/hokkaido_indicator_zero_carbon_evidence_packets.json";

export type HokkaidoIndicatorValue = {
  role: "current" | "intermediate_target" | "final_target";
  period: string | null;
  value: number | null;
  status: "numeric" | "not_set" | "not_available";
  operator?: "exact" | "at_least" | "at_most";
  value_text_original: string;
};
export type HokkaidoIndicatorSeries = { label: string | null; unit_original: string; temporal_scope: "calendar_year" | "fiscal_year" | "snapshot" | "other"; values: HokkaidoIndicatorValue[] };
export type HokkaidoIndicator = { id: string; indicator_number: number; indicator_name_original: string; policy_direction_id: string; policy_field_ids: string[]; policy_orientation_original: string; indicator_explanation_original: string; source_page: number; series: HokkaidoIndicatorSeries[]; target_setting_status: "set" | "not_set" | "partially_set"; target_setting_rationale_original: string; comparability_note_original: string | null; actual_linkage_status: "not_linked"; evaluation_status: "not_assessed"; review_status: "reviewed"; confidence: "high" };

export const hokkaidoFoodIndicatorCatalog = foodCatalog;
export const hokkaidoFoodIndicators = foodCatalog.items as HokkaidoIndicator[];
export const hokkaidoFoodIndicatorEvidence = foodEvidence;
export const hokkaidoTourismIndicatorCatalog = tourismCatalog;
export const hokkaidoTourismIndicators = tourismCatalog.items as HokkaidoIndicator[];
export const hokkaidoTourismIndicatorEvidence = tourismEvidence;
export const hokkaidoZeroCarbonIndicatorCatalog = zeroCarbonCatalog;
export const hokkaidoZeroCarbonIndicators = zeroCarbonCatalog.items as HokkaidoIndicator[];
export const hokkaidoZeroCarbonIndicatorEvidence = zeroCarbonEvidence;

export const hokkaidoReviewedIndicators = [
  ...hokkaidoFoodIndicators,
  ...hokkaidoTourismIndicators,
  ...hokkaidoZeroCarbonIndicators,
].sort((left, right) => left.indicator_number - right.indicator_number);
export const hokkaidoIndicatorEvidencePackets = [
  ...hokkaidoFoodIndicatorEvidence,
  ...hokkaidoTourismIndicatorEvidence,
  ...hokkaidoZeroCarbonIndicatorEvidence,
];

export const hokkaidoIndicatorReviewStats = {
  reviewedIndicators: hokkaidoReviewedIndicators.length,
  remainingIndicators: 108 - hokkaidoReviewedIndicators.length,
  evidencePackets: hokkaidoIndicatorEvidencePackets.length,
  targetSet: hokkaidoReviewedIndicators.filter((indicator) => indicator.target_setting_status === "set").length,
  targetNotSet: hokkaidoReviewedIndicators.filter((indicator) => indicator.target_setting_status === "not_set").length,
  comparabilityWarnings: hokkaidoReviewedIndicators.filter((indicator) => indicator.comparability_note_original?.includes("単純比較")).length,
  notAvailableCurrentValues: hokkaidoReviewedIndicators.reduce((total, indicator) => total + indicator.series.filter((series) => series.values[0]?.status === "not_available").length, 0),
  boundedFinalTargets: hokkaidoReviewedIndicators.reduce((total, indicator) => total + indicator.series.filter((series) => series.values[2]?.operator === "at_least").length, 0),
  crossFieldIndicators: hokkaidoReviewedIndicators.filter((indicator) => indicator.policy_field_ids.length > 1).length,
};
