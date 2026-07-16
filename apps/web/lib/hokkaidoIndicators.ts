import childrenParentingCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_children_parenting.json";
import digitalCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_digital.json";
import educationLearningCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_education_learning.json";
import employmentWorkCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_employment_work.json";
import foodCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_food.json";
import globalizationCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_globalization.json";
import industryCrossSectorCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_industry_cross_sector.json";
import infrastructureCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_infrastructure.json";
import manufacturingGrowthCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_manufacturing_growth.json";
import medicalWelfareCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_medical_welfare.json";
import regionalDevelopmentCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_regional_development.json";
import resilienceCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_resilience.json";
import safetySecurityCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_safety_security.json";
import smeCommerceCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_sme_commerce.json";
import tourismCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_tourism.json";
import zeroCarbonCatalog from "../../../data/entities/policy/hokkaido_indicator_catalog_zero_carbon.json";
import childrenParentingEvidence from "../../../data/entities/policy/hokkaido_indicator_children_parenting_evidence_packets.json";
import digitalEvidence from "../../../data/entities/policy/hokkaido_indicator_digital_evidence_packets.json";
import educationLearningEvidence from "../../../data/entities/policy/hokkaido_indicator_education_learning_evidence_packets.json";
import employmentWorkEvidence from "../../../data/entities/policy/hokkaido_indicator_employment_work_evidence_packets.json";
import foodEvidence from "../../../data/entities/policy/hokkaido_indicator_food_evidence_packets.json";
import globalizationEvidence from "../../../data/entities/policy/hokkaido_indicator_globalization_evidence_packets.json";
import industryCrossSectorEvidence from "../../../data/entities/policy/hokkaido_indicator_industry_cross_sector_evidence_packets.json";
import infrastructureEvidence from "../../../data/entities/policy/hokkaido_indicator_infrastructure_evidence_packets.json";
import manufacturingGrowthEvidence from "../../../data/entities/policy/hokkaido_indicator_manufacturing_growth_evidence_packets.json";
import medicalWelfareEvidence from "../../../data/entities/policy/hokkaido_indicator_medical_welfare_evidence_packets.json";
import regionalDevelopmentEvidence from "../../../data/entities/policy/hokkaido_indicator_regional_development_evidence_packets.json";
import resilienceEvidence from "../../../data/entities/policy/hokkaido_indicator_resilience_evidence_packets.json";
import safetySecurityEvidence from "../../../data/entities/policy/hokkaido_indicator_safety_security_evidence_packets.json";
import smeCommerceEvidence from "../../../data/entities/policy/hokkaido_indicator_sme_commerce_evidence_packets.json";
import tourismEvidence from "../../../data/entities/policy/hokkaido_indicator_tourism_evidence_packets.json";
import zeroCarbonEvidence from "../../../data/entities/policy/hokkaido_indicator_zero_carbon_evidence_packets.json";

export type HokkaidoIndicatorValue = {
  role: "current" | "intermediate_target" | "final_target";
  period: string | null;
  value: number | null;
  status: "numeric" | "conditional" | "not_set" | "not_available";
  operator?: "exact" | "at_least" | "at_most";
  aggregation_scope?: "single_period" | "multi_year_cumulative" | "cumulative_to_date" | "snapshot";
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

type CatalogShape = {
  id: string;
  policy_field_id: string;
  source_document_url: string;
  reviewed_at: string;
  indicator_number_start: number;
  indicator_number_end: number;
  items: unknown[];
};

const groupDefinitions: Array<{ catalog: CatalogShape; label: string; evidence: unknown[] }> = [
  { catalog: foodCatalog, label: "食", evidence: foodEvidence },
  { catalog: tourismCatalog, label: "観光", evidence: tourismEvidence },
  { catalog: zeroCarbonCatalog, label: "ゼロカーボン", evidence: zeroCarbonEvidence },
  { catalog: digitalCatalog, label: "デジタル", evidence: digitalEvidence },
  { catalog: manufacturingGrowthCatalog, label: "ものづくり・成長分野", evidence: manufacturingGrowthEvidence },
  { catalog: industryCrossSectorCatalog, label: "産業活性化・業種横断分野", evidence: industryCrossSectorEvidence },
  { catalog: childrenParentingCatalog, label: "子ども・子育て", evidence: childrenParentingEvidence },
  { catalog: educationLearningCatalog, label: "教育・学び", evidence: educationLearningEvidence },
  { catalog: medicalWelfareCatalog, label: "医療・福祉", evidence: medicalWelfareEvidence },
  { catalog: employmentWorkCatalog, label: "就業・就労環境", evidence: employmentWorkEvidence },
  { catalog: smeCommerceCatalog, label: "中小企業・商業", evidence: smeCommerceEvidence },
  { catalog: safetySecurityCatalog, label: "安全・安心", evidence: safetySecurityEvidence },
  { catalog: regionalDevelopmentCatalog, label: "地域づくり", evidence: regionalDevelopmentEvidence },
  { catalog: globalizationCatalog, label: "グローバル化", evidence: globalizationEvidence },
  { catalog: resilienceCatalog, label: "北海道の強靱化", evidence: resilienceEvidence },
  { catalog: infrastructureCatalog, label: "社会経済の基盤整備", evidence: infrastructureEvidence },
];

export const hokkaidoIndicatorGroups: HokkaidoIndicatorGroup[] = groupDefinitions.map(
  ({ catalog, label }) => ({
    id: catalog.id,
    fieldId: catalog.policy_field_id,
    label,
    sourceDocumentUrl: catalog.source_document_url,
    reviewedAt: catalog.reviewed_at,
    indicatorNumberStart: catalog.indicator_number_start,
    indicatorNumberEnd: catalog.indicator_number_end,
    indicators: catalog.items as HokkaidoIndicator[],
  }),
);

export const hokkaidoReviewedIndicators = hokkaidoIndicatorGroups
  .flatMap((group) => group.indicators)
  .sort((left, right) => left.indicator_number - right.indicator_number);

export const hokkaidoIndicatorEvidencePackets = groupDefinitions.flatMap(({ evidence }) => evidence);

export const hokkaidoIndicatorReviewStats = {
  reviewedIndicators: hokkaidoReviewedIndicators.length,
  remainingIndicators: 108 - hokkaidoReviewedIndicators.length,
  evidencePackets: hokkaidoIndicatorEvidencePackets.length,
  targetSet: hokkaidoReviewedIndicators.filter((item) => item.target_setting_status === "set").length,
  targetNotSet: hokkaidoReviewedIndicators.filter((item) => item.target_setting_status === "not_set").length,
  partialTargets: hokkaidoReviewedIndicators.filter((item) => item.target_setting_status === "partially_set").length,
  conditionalTargetValues: hokkaidoReviewedIndicators.reduce(
    (total, item) => total + item.series.reduce(
      (seriesTotal, series) => seriesTotal + series.values.filter((value) => value.status === "conditional").length,
      0,
    ),
    0,
  ),
  comparabilityWarnings: hokkaidoReviewedIndicators.filter((item) => item.comparability_note_original !== null).length,
  unavailableCurrentSeries: hokkaidoReviewedIndicators.reduce(
    (total, item) => total + item.series.filter((series) => series.values[0]?.status === "not_available").length,
    0,
  ),
  multiYearCumulativeSeries: hokkaidoReviewedIndicators.reduce(
    (total, item) => total + item.series.filter((series) =>
      series.values.some((value) => value.aggregation_scope === "multi_year_cumulative"),
    ).length,
    0,
  ),
  cumulativeToDateSeries: hokkaidoReviewedIndicators.reduce(
    (total, item) => total + item.series.filter((series) =>
      series.values.some((value) => value.aggregation_scope === "cumulative_to_date"),
    ).length,
    0,
  ),
  crossFieldIndicators: hokkaidoReviewedIndicators.filter((item) => item.policy_field_ids.length > 1).length,
};
