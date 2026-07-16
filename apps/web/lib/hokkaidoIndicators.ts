import foodCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_food.json";
import foodEvidence from "../../../data/entities/policy/hokkaido_indicator_food_evidence_packets.json";

export type HokkaidoIndicatorValue = {
  role: "current" | "intermediate_target" | "final_target";
  period: string | null;
  value: number | null;
  status: "numeric" | "not_set" | "not_available";
  value_text_original: string;
};

export type HokkaidoIndicatorSeries = {
  label: string | null;
  unit_original: string;
  temporal_scope: "calendar_year" | "fiscal_year" | "snapshot" | "other";
  values: HokkaidoIndicatorValue[];
};

export type HokkaidoIndicator = {
  id: string;
  indicator_number: number;
  indicator_name_original: string;
  policy_direction_id: string;
  policy_field_ids: string[];
  policy_orientation_original: string;
  indicator_explanation_original: string;
  source_page: number;
  series: HokkaidoIndicatorSeries[];
  target_setting_status: "set" | "not_set" | "partially_set";
  target_setting_rationale_original: string;
  comparability_note_original: string | null;
  actual_linkage_status: "not_linked";
  evaluation_status: "not_assessed";
  review_status: "reviewed";
  confidence: "high";
};

export const hokkaidoFoodIndicatorCatalog = foodCatalog;
export const hokkaidoFoodIndicators = foodCatalog.items as HokkaidoIndicator[];
export const hokkaidoFoodIndicatorEvidence = foodEvidence;

export const hokkaidoIndicatorReviewStats = {
  reviewedIndicators: hokkaidoFoodIndicators.length,
  remainingIndicators: 108 - hokkaidoFoodIndicators.length,
  evidencePackets: hokkaidoFoodIndicatorEvidence.length,
  targetSet: hokkaidoFoodIndicators.filter(
    (indicator) => indicator.target_setting_status === "set",
  ).length,
  targetNotSet: hokkaidoFoodIndicators.filter(
    (indicator) => indicator.target_setting_status === "not_set",
  ).length,
  comparabilityWarnings: hokkaidoFoodIndicators.filter(
    (indicator) => indicator.comparability_note_original !== null,
  ).length,
};
