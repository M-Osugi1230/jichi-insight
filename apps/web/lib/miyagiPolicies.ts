import indicatorIndex from "../../../data/catalog/miyagi_indicator_source_index.json";
import sources from "../../../data/catalog/miyagi_policy_sources.json";
import manifest from "../../../data/catalog/miyagi_policy_review_manifest.json";
import kpiCatalog from "../../../data/entities/policy/miyagi_kpi_catalog_groups_1_23.json";
import kpiEvidence from "../../../data/entities/policy/miyagi_kpi_groups_1_23_evidence_packets.json";
import directionEvidence from "../../../data/entities/policy/miyagi_policy_direction_evidence_packets.json";
import hierarchy from "../../../data/entities/policy/miyagi_policy_hierarchy.json";

export type MiyagiIndicatorValue = {
  role: "initial" | "current" | "intermediate_target" | "final_target";
  period: string;
  value: number | null;
  status: "numeric" | "conditional" | "not_set" | "not_available";
  operator?: "exact" | "at_least" | "at_most";
  aggregation_scope:
    | "single_period"
    | "multi_year_cumulative"
    | "cumulative_to_date"
    | "snapshot";
  value_text_original: string;
};

export type MiyagiIndicatorSeries = {
  label: string | null;
  unit_original: string;
  temporal_scope: "calendar_year" | "fiscal_year" | "snapshot" | "other";
  values: MiyagiIndicatorValue[];
};

export type MiyagiIndicator = {
  id: string;
  target_group_number: number;
  series_number: number;
  indicator_name_original: string;
  scope_type: "pillar" | "measure";
  scope_number: number;
  policy_direction_id: string;
  policy_id: string | null;
  measure_id: string | null;
  source_pdf_page: number;
  source_printed_page: number;
  sdg_goal_numbers: number[];
  series: MiyagiIndicatorSeries[];
  target_setting_status: "set" | "not_set" | "partially_set";
  comparability_note_original: string;
  actual_linkage_status: "not_linked";
  evaluation_status: "not_assessed";
  review_status: "reviewed";
  confidence: "high";
};

const policies = hierarchy.directions.flatMap((direction) => direction.policies);
const measures = policies.flatMap((policy) => policy.measures);

export const reviewedMiyagiPolicyHierarchy = hierarchy;
export const reviewedMiyagiPolicyDirections = hierarchy.directions;
export const miyagiReviewedIndicators = (kpiCatalog.items as MiyagiIndicator[]).sort(
  (left, right) => left.target_group_number - right.target_group_number,
);
export const miyagiKpiEvidencePackets = kpiEvidence;

export const miyagiIndicatorScopes = [
  {
    id: "pillar-1",
    label: "柱1",
    title: hierarchy.directions[0].title_original,
    indicators: miyagiReviewedIndicators.filter(
      (indicator) => indicator.scope_type === "pillar" && indicator.scope_number === 1,
    ),
  },
  ...hierarchy.directions[0].policies[0].measures.slice(0, 3).map((measure) => ({
    id: measure.id,
    label: `取組${measure.measure_number}`,
    title: measure.title_original,
    indicators: miyagiReviewedIndicators.filter(
      (indicator) => indicator.measure_id === measure.id,
    ),
  })),
];

export const miyagiPolicyReviewStats = {
  sources: sources.records.length,
  reviewedSources: sources.records.filter(
    (source) => source.review_status === "reviewed",
  ).length,
  directions: hierarchy.directions.length,
  policies: policies.length,
  measures: measures.length,
  recoveryAreas: hierarchy.recovery_support_areas.length,
  evidencePackets: directionEvidence.length,
  hierarchyEvidencePackets: directionEvidence.length,
  implementationPeriod:
    `${hierarchy.implementation_period_start}〜${hierarchy.implementation_period_end}年度`,
  targetGroups: indicatorIndex.target_group_count,
  indicatorSeries: indicatorIndex.indicator_series_count,
  multiSeriesGroups: indicatorIndex.multi_series_group_count,
  additionalSeries: indicatorIndex.additional_series_count,
  sourcePages:
    indicatorIndex.source_pdf_page_end - indicatorIndex.source_pdf_page_start + 1,
  expectedKpiCount: manifest.expected_kpi_count,
  kpiCountStatus: manifest.kpi_count_status,
  activeWorkPackage: manifest.active_work_package,
  contentReviewStatus: indicatorIndex.content_review_status,
  reviewedTargetGroups: miyagiReviewedIndicators.length,
  reviewedIndicatorSeries: miyagiReviewedIndicators.reduce(
    (total, indicator) => total + indicator.series.length,
    0,
  ),
  remainingTargetGroups:
    indicatorIndex.target_group_count - miyagiReviewedIndicators.length,
  kpiEvidencePackets: kpiEvidence.length,
  fullySetTargets: miyagiReviewedIndicators.filter(
    (indicator) => indicator.target_setting_status === "set",
  ).length,
  partiallySetTargets: miyagiReviewedIndicators.filter(
    (indicator) => indicator.target_setting_status === "partially_set",
  ).length,
  cumulativeTargets: miyagiReviewedIndicators.filter((indicator) =>
    indicator.series.some((series) =>
      series.values.some(
        (value) => value.aggregation_scope === "cumulative_to_date",
      ),
    ),
  ).length,
};
