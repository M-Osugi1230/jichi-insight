import childrenParentingCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_children_parenting.json";
import digitalCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_digital.json";
import foodCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_food.json";
import industryCrossSectorCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_industry_cross_sector.json";
import manufacturingGrowthCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_manufacturing_growth.json";
import tourismCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_tourism.json";
import zeroCarbonCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_zero_carbon.json";
import childrenParentingEvidence from "../../../data/entities/policy/hokkaido_indicator_children_parenting_evidence_packets.json";
import digitalEvidence from "../../../data/entities/policy/hokkaido_indicator_digital_evidence_packets.json";
import foodEvidence from "../../../data/entities/policy/hokkaido_indicator_food_evidence_packets.json";
import industryCrossSectorEvidence from "../../../data/entities/policy/hokkaido_indicator_industry_cross_sector_evidence_packets.json";
import manufacturingGrowthEvidence from "../../../data/entities/policy/hokkaido_indicator_manufacturing_growth_evidence_packets.json";
import tourismEvidence from "../../../data/entities/policy/hokkaido_indicator_tourism_evidence_packets.json";
import zeroCarbonEvidence from "../../../data/entities/policy/hokkaido_indicator_zero_carbon_evidence_packets.json";

export type HokkaidoIndicatorValue = {
  role: "current" | "intermediate_target" | "final_target";
  period: string | null;
  value: number | null;
  status: "numeric" | "conditional" | "not_set" | "not_available";
  operator?: "exact" | "at_least" | "at_most";
  aggregation_scope?:
    | "single_period"
    | "multi_year_cumulative"
    | "cumulative_to_date"
    | "snapshot";
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
export const hokkaidoIndustryCrossSectorIndicators =
  industryCrossSectorCatalog.items as HokkaidoIndicator[];
export const hokkaidoChildrenParentingIndicators =
  childrenParentingCatalog.items as HokkaidoIndicator[];

export const hokkaidoReviewedIndicators = [
  ...hokkaidoFoodIndicators,
  ...hokkaidoTourismIndicators,
  ...hokkaidoZeroCarbonIndicators,
  ...hokkaidoDigitalIndicators,
  ...hokkaidoManufacturingGrowthIndicators,
  ...hokkaidoIndustryCrossSectorIndicators,
  ...hokkaidoChildrenParentingIndicators,
].sort((left, right) => left.indicator_number - right.indicator_number);

export const hokkaidoIndicatorEvidencePackets = [
  ...foodEvidence,
  ...tourismEvidence,
  ...zeroCarbonEvidence,
  ...digitalEvidence,
  ...manufacturingGrowthEvidence,
  ...industryCrossSectorEvidence,
  ...childrenParentingEvidence,
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
  conditionalTargetValues: hokkaidoReviewedIndicators.reduce(
    (total, indicator) =>
      total +
      indicator.series.reduce(
        (seriesTotal, series) =>
          seriesTotal +
          series.values.filter((value) => value.status === "conditional").length,
        0,
      ),
    0,
  ),
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
  cumulativeToDateSeries: hokkaidoReviewedIndicators.reduce(
    (total, indicator) =>
      total +
      indicator.series.filter((series) =>
        series.values.some((value) => value.aggregation_scope === "cumulative_to_date"),
      ).length,
    0,
  ),
  crossFieldIndicators: hokkaidoReviewedIndicators.filter(
    (indicator) => indicator.policy_field_ids.length > 1,
  ).length,
};
