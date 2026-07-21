import indicatorCatalog from "../../../data/reviewed/osaka_beyond_expo_indicators.json";
import reviewManifest from "../../../data/catalog/osaka_beyond_expo_indicator_review_manifest.json";
import policySources from "../../../data/catalog/osaka_policy_sources.json";

export type OsakaIndicatorValue = {
  role: "baseline" | "current" | "target";
  period: string;
  value: number | string | null;
  value_text_original: string;
  status: "numeric" | "missing";
  operator: "exact" | "not_applicable";
  aggregation_scope: "single_period" | "snapshot" | "cumulative" | "rank";
};

export type OsakaIndicatorSeries = {
  label_original: string | null;
  unit_original: string;
  direction: "increase" | "decrease";
  values: OsakaIndicatorValue[];
};

export type OsakaIndicator = {
  id: string;
  display_order: number;
  indicator_layer: "strategy_target" | "objective_kpi" | "subjective_wellbeing";
  pillar_original: string;
  category_original: string;
  indicator_name_original: string;
  source_page: number;
  response_scale: "0_to_10" | "1_to_5" | "1_to_5_reversed" | null;
  series: OsakaIndicatorSeries[];
  comparability_note_original: string;
  legacy_vision_linkage_status: "separate_lineage";
  business_list_linkage_status: "not_linked";
  policy_achievement_assessment_status: "not_assessed";
  review_status: "reviewed";
};

export type OsakaPolicySource = {
  id: string;
  category: string;
  title: string;
  url: string;
  publication_date: string;
  review_status: string;
  role_note: string;
};

export const reviewedOsakaIndicators = indicatorCatalog.items as OsakaIndicator[];
export const osakaPolicySources = policySources.records as OsakaPolicySource[];
export const osakaIndicatorReviewManifest = reviewManifest;

export const osakaIndicatorPillars = Array.from(
  new Set(reviewedOsakaIndicators.map((item) => item.pillar_original)),
);

export const osakaIndicatorStats = {
  indicatorRows: reviewManifest.reviewed_indicator_row_count,
  indicatorSeries: reviewManifest.reviewed_indicator_series_count,
  evidencePackets: reviewManifest.evidence_packet_count,
  strategyTargets: reviewManifest.strategy_target_count,
  objectiveKpis: reviewManifest.objective_kpi_count,
  subjectiveIndicators: reviewManifest.subjective_indicator_count,
  subjectiveWithCurrentValue: reviewManifest.subjective_indicators_with_2024_value,
  subjectivePendingSurvey: reviewManifest.subjective_indicators_pending_first_survey,
  legacyLinkedSeries: reviewManifest.legacy_vision_linked_series_count,
  businessLinkedIndicators: reviewManifest.business_list_linked_indicator_count,
  assessedIndicators: reviewManifest.policy_achievement_assessed_indicator_count,
};

export const osakaLayerLabels: Record<OsakaIndicator["indicator_layer"], string> = {
  strategy_target: "戦略目標",
  objective_kpi: "客観KPI",
  subjective_wellbeing: "主観・Well-Being",
};

export const osakaValueRoleLabels: Record<OsakaIndicatorValue["role"], string> = {
  baseline: "2023年",
  current: "最新値",
  target: "目標",
};
