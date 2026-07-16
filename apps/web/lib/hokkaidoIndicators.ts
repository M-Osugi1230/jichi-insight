import childrenParentingCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_children_parenting.json";
import digitalCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_digital.json";
import educationLearningCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_education_learning.json";
import foodCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_food.json";
import industryCrossSectorCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_industry_cross_sector.json";
import manufacturingGrowthCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_manufacturing_growth.json";
import medicalWelfareCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_medical_welfare.json";
import tourismCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_tourism.json";
import zeroCarbonCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_zero_carbon.json";
import childrenParentingEvidence from "../../../data/entities/policy/hokkaido_indicator_children_parenting_evidence_packets.json";
import digitalEvidence from "../../../data/entities/policy/hokkaido_indicator_digital_evidence_packets.json";
import educationLearningEvidence from "../../../data/entities/policy/hokkaido_indicator_education_learning_evidence_packets.json";
import foodEvidence from "../../../data/entities/policy/hokkaido_indicator_food_evidence_packets.json";
import industryCrossSectorEvidence from "../../../data/entities/policy/hokkaido_indicator_industry_cross_sector_evidence_packets.json";
import manufacturingGrowthEvidence from "../../../data/entities/policy/hokkaido_indicator_manufacturing_growth_evidence_packets.json";
import medicalWelfareEvidence from "../../../data/entities/policy/hokkaido_indicator_medical_welfare_evidence_packets.json";
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

export type HokkaidoIndicatorGroup = {
  id: string;
  fieldId: string;
  label: string;
  sourceDocumentUrl: string;
  reviewedAt: string;
  indicatorNumberStart: number;
  indicatorNumberEnd: number;
  indicators: HokkaidoIndicator[];
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
export const hokkaidoEducationLearningIndicators =
  educationLearningCatalog.items as HokkaidoIndicator[];
export const hokkaidoMedicalWelfareIndicators =
  medicalWelfareCatalog.items as HokkaidoIndicator[];

export const hokkaidoIndicatorGroups: HokkaidoIndicatorGroup[] = [
  {
    id: foodCatalog.id,
    fieldId: foodCatalog.policy_field_id,
    label: "食",
    sourceDocumentUrl: foodCatalog.source_document_url,
    reviewedAt: foodCatalog.reviewed_at,
    indicatorNumberStart: foodCatalog.indicator_number_start,
    indicatorNumberEnd: foodCatalog.indicator_number_end,
    indicators: hokkaidoFoodIndicators,
  },
  {
    id: tourismCatalog.id,
    fieldId: tourismCatalog.policy_field_id,
    label: "観光",
    sourceDocumentUrl: tourismCatalog.source_document_url,
    reviewedAt: tourismCatalog.reviewed_at,
    indicatorNumberStart: tourismCatalog.indicator_number_start,
    indicatorNumberEnd: tourismCatalog.indicator_number_end,
    indicators: hokkaidoTourismIndicators,
  },
  {
    id: zeroCarbonCatalog.id,
    fieldId: zeroCarbonCatalog.policy_field_id,
    label: "ゼロカーボン",
    sourceDocumentUrl: zeroCarbonCatalog.source_document_url,
    reviewedAt: zeroCarbonCatalog.reviewed_at,
    indicatorNumberStart: zeroCarbonCatalog.indicator_number_start,
    indicatorNumberEnd: zeroCarbonCatalog.indicator_number_end,
    indicators: hokkaidoZeroCarbonIndicators,
  },
  {
    id: digitalCatalog.id,
    fieldId: digitalCatalog.policy_field_id,
    label: "デジタル",
    sourceDocumentUrl: digitalCatalog.source_document_url,
    reviewedAt: digitalCatalog.reviewed_at,
    indicatorNumberStart: digitalCatalog.indicator_number_start,
    indicatorNumberEnd: digitalCatalog.indicator_number_end,
    indicators: hokkaidoDigitalIndicators,
  },
  {
    id: manufacturingGrowthCatalog.id,
    fieldId: manufacturingGrowthCatalog.policy_field_id,
    label: "ものづくり・成長分野",
    sourceDocumentUrl: manufacturingGrowthCatalog.source_document_url,
    reviewedAt: manufacturingGrowthCatalog.reviewed_at,
    indicatorNumberStart: manufacturingGrowthCatalog.indicator_number_start,
    indicatorNumberEnd: manufacturingGrowthCatalog.indicator_number_end,
    indicators: hokkaidoManufacturingGrowthIndicators,
  },
  {
    id: industryCrossSectorCatalog.id,
    fieldId: industryCrossSectorCatalog.policy_field_id,
    label: "産業活性化・業種横断分野",
    sourceDocumentUrl: industryCrossSectorCatalog.source_document_url,
    reviewedAt: industryCrossSectorCatalog.reviewed_at,
    indicatorNumberStart: industryCrossSectorCatalog.indicator_number_start,
    indicatorNumberEnd: industryCrossSectorCatalog.indicator_number_end,
    indicators: hokkaidoIndustryCrossSectorIndicators,
  },
  {
    id: childrenParentingCatalog.id,
    fieldId: childrenParentingCatalog.policy_field_id,
    label: "子ども・子育て",
    sourceDocumentUrl: childrenParentingCatalog.source_document_url,
    reviewedAt: childrenParentingCatalog.reviewed_at,
    indicatorNumberStart: childrenParentingCatalog.indicator_number_start,
    indicatorNumberEnd: childrenParentingCatalog.indicator_number_end,
    indicators: hokkaidoChildrenParentingIndicators,
  },
  {
    id: educationLearningCatalog.id,
    fieldId: educationLearningCatalog.policy_field_id,
    label: "教育・学び",
    sourceDocumentUrl: educationLearningCatalog.source_document_url,
    reviewedAt: educationLearningCatalog.reviewed_at,
    indicatorNumberStart: educationLearningCatalog.indicator_number_start,
    indicatorNumberEnd: educationLearningCatalog.indicator_number_end,
    indicators: hokkaidoEducationLearningIndicators,
  },
  {
    id: medicalWelfareCatalog.id,
    fieldId: medicalWelfareCatalog.policy_field_id,
    label: "医療・福祉",
    sourceDocumentUrl: medicalWelfareCatalog.source_document_url,
    reviewedAt: medicalWelfareCatalog.reviewed_at,
    indicatorNumberStart: medicalWelfareCatalog.indicator_number_start,
    indicatorNumberEnd: medicalWelfareCatalog.indicator_number_end,
    indicators: hokkaidoMedicalWelfareIndicators,
  },
];

export const hokkaidoReviewedIndicators = [
  ...hokkaidoFoodIndicators,
  ...hokkaidoTourismIndicators,
  ...hokkaidoZeroCarbonIndicators,
  ...hokkaidoDigitalIndicators,
  ...hokkaidoManufacturingGrowthIndicators,
  ...hokkaidoIndustryCrossSectorIndicators,
  ...hokkaidoChildrenParentingIndicators,
  ...hokkaidoEducationLearningIndicators,
  ...hokkaidoMedicalWelfareIndicators,
].sort((left, right) => left.indicator_number - right.indicator_number);

export const hokkaidoIndicatorEvidencePackets = [
  ...foodEvidence,
  ...tourismEvidence,
  ...zeroCarbonEvidence,
  ...digitalEvidence,
  ...manufacturingGrowthEvidence,
  ...industryCrossSectorEvidence,
  ...childrenParentingEvidence,
  ...educationLearningEvidence,
  ...medicalWelfareEvidence,
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
