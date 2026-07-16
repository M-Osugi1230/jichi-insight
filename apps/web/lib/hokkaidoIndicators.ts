import digitalCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_digital.json";
import foodCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_food.json";
import manufacturingGrowthCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_manufacturing_growth.json";
import tourismCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_tourism.json";
import zeroCarbonCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_zero_carbon.json";
import digitalEvidence from "../../../data/entities/policy/hokkaido_indicator_digital_evidence_packets.json";
import foodEvidence from "../../../data/entities/policy/hokkaido_indicator_food_evidence_packets.json";
import manufacturingGrowthEvidence from "../../../data/entities/policy/hokkaido_indicator_manufacturing_growth_evidence_packets.json";
import tourismEvidence from "../../../data/entities/policy/hokkaido_indicator_tourism_evidence_packets.json";
import zeroCarbonEvidence from "../../../data/entities/policy/hokkaido_indicator_zero_carbon_evidence_packets.json";

export type HokkaidoIndicatorValue = {
  role: "current" | "intermediate_target" | "final_target";
  period: string | null;
  value: number | null;
  status: "numeric" | "not_set" | "not_available";
  operator?: "exact" | "at_least" | "at_most";
  aggregation_scope?: "single_period" | "multi_year_cumulative" | "snapshot" | "other";
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

export const hokkaidoFoodIndicators = foodCatalog.items as HokkaidoIndicator[];
export const hokkaidoTourismIndicators = tourismCatalog.items as HokkaidoIndicator[];
export const hokkaidoZeroCarbonIndicators = zeroCarbonCatalog.items as HokkaidoIndicator[];
export const hokkaidoDigitalIndicators = digitalCatalog.items as HokkaidoIndicator[];
export const hokkaidoManufacturingGrowthIndicators =
  manufacturingGrowthCatalog.items as HokkaidoIndicator[];

export const hokkaidoReviewedIndicators = [
  ...hokkaidoFoodIndicators,
  ...hokkaidoTourismIndicators,
  ...hokkaidoZeroCarbonIndicators,
  ...hokkaidoDigitalIndicators,
  ...hokkaidoManufacturingGrowthIndicators,
].sort((left, right) => left.indicator_number - right.indicator_number);

export const hokkaidoIndicatorEvidencePackets = [
  ...foodEvidence,
  ...tourismEvidence,
  ...zeroCarbonEvidence,
  ...digitalEvidence,
  ...manufacturingGrowthEvidence,
];

export const hokkaidoIndicatorReviewStats = {
  reviewedIndicators: hokkaidoReviewedIndicators.length,
  remainingIndicators: 108 - hokkaidoReviewedIndicators.length,
  evidencePackets: hokkaidoIndicatorEvidencePackets.length,
  targetSet: hokkaidoReviewedIndicators.filter(
    (indicator) => indicator.target_setting_status === "set",
  ).length,
  targetNotSet: hokkaidoReviewedIndicators.filter(
    (indicator) => indicator.target_setting_status === "not_set",
  ).length,
  partialTargets: hokkaidoReviewedIndicators.filter(
    (indicator) => indicator.target_setting_status === "partially_set",
  ).length,
  comparabilityWarnings: hokkaidoReviewedIndicators.filter(
    (indicator) => indicator.comparability_note_original !== null,
  ).length,
  unavailableCurrentSeries: hokkaidoReviewedIndicators.reduce(
    (total, indicator) =>
      total +
      indicator.series.filter((series) => series.values[0]?.status === "not_available")
        .length,
    0,
  ),
  multiYearCumulativeSeries: hokkaidoReviewedIndicators.reduce(
    (total, indicator) =>
      total +
      indicator.series.filter((series) =>
        series.values.some((value) => value.aggregation_scope === "multi_year_cumulative"),
      ).length,
    0,
  ),
  crossFieldIndicators: hokkaidoReviewedIndicators.filter(
    (indicator) => indicator.policy_field_ids.length > 1,
  ).length,
};
