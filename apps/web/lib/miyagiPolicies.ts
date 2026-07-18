import indicatorIndex from "../../../data/catalog/miyagi_indicator_source_index.json";
import sources from "../../../data/catalog/miyagi_policy_sources.json";
import manifest from "../../../data/catalog/miyagi_policy_review_manifest.json";
import measure1Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure1.json";
import measure2Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure2.json";
import measure3Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure3.json";
import measure4aCatalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure4a.json";
import measure4bCatalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure4b.json";
import measure5aCatalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure5a.json";
import measure5bCatalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure5b.json";
import pillar1Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_pillar1.json";
import group32Evidence from "../../../data/entities/policy/miyagi_kpi_group32_evidence_packet.json";
import groups33_34Evidence from "../../../data/entities/policy/miyagi_kpi_groups33_34_evidence_packets.json";
import group35Evidence from "../../../data/entities/policy/miyagi_kpi_group35_evidence_packet.json";
import group36Evidence from "../../../data/entities/policy/miyagi_kpi_group36_evidence_packet.json";
import measure1Evidence from "../../../data/entities/policy/miyagi_kpi_measure1_evidence_packets.json";
import measure2Evidence from "../../../data/entities/policy/miyagi_kpi_measure2_evidence_packets.json";
import measure3aEvidence from "../../../data/entities/policy/miyagi_kpi_measure3a_evidence_packets.json";
import measure3bEvidence from "../../../data/entities/policy/miyagi_kpi_measure3b_evidence_packets.json";
import measure4aEvidence from "../../../data/entities/policy/miyagi_kpi_measure4a_evidence_packets.json";
import measure4bEvidence from "../../../data/entities/policy/miyagi_kpi_measure4b_evidence_packets.json";
import measure5TailEvidence from "../../../data/entities/policy/miyagi_kpi_measure5_tail_evidence_packets.json";
import pillar1Evidence from "../../../data/entities/policy/miyagi_kpi_pillar1_evidence_packets.json";
import directionEvidence from "../../../data/entities/policy/miyagi_policy_direction_evidence_packets.json";
import hierarchy from "../../../data/entities/policy/miyagi_policy_hierarchy.json";

export type MiyagiKpiValue = {
  role: "initial" | "current" | "midterm_target" | "late_target";
  period_original: "R3" | "R4" | "R5" | "R6" | "R9" | "R12";
  period_year: number;
  value: number | null;
  status: "numeric" | "not_set" | "not_available" | "conditional";
  operator?: "exact" | "at_least" | "at_most";
  value_text_original: string;
};

export type MiyagiKpiSeries = {
  id: string;
  series_number: number;
  indicator_name_original: string;
  unit_original: string;
  aggregation_scope: "single_period" | "cumulative_to_date";
  values: MiyagiKpiValue[];
};

export type MiyagiKpiGroup = {
  id: string;
  target_group_number: number;
  scope_type: "pillar" | "measure";
  scope_number: number;
  source_page: number;
  printed_page: number;
  sdg_goal_numbers: number[];
  series: MiyagiKpiSeries[];
  target_setting_status: "set" | "partially_set" | "not_set";
  comparability_note_original: string | null;
  actual_linkage_status: "not_linked";
  evaluation_status: "not_assessed";
  review_status: "reviewed";
  confidence: "high";
};

const policies = hierarchy.directions.flatMap((direction) => direction.policies);
const measures = policies.flatMap((policy) => policy.measures);
const reviewedGroups = [
  ...pillar1Catalog.items,
  ...measure1Catalog.items,
  ...measure2Catalog.items,
  ...measure3Catalog.items,
  ...measure4aCatalog.items,
  ...measure4bCatalog.items,
  ...measure5aCatalog.items,
  ...measure5bCatalog.items,
] as MiyagiKpiGroup[];
const reviewedSeries = reviewedGroups.flatMap((group) => group.series);
const kpiEvidence = [
  ...pillar1Evidence,
  ...measure1Evidence,
  ...measure2Evidence,
  ...measure3aEvidence,
  ...measure3bEvidence,
  ...measure4aEvidence,
  ...measure4bEvidence,
  ...group32Evidence,
  ...groups33_34Evidence,
  ...group35Evidence,
  ...group36Evidence,
  ...measure5TailEvidence,
];

function numericValue(series: MiyagiKpiSeries, role: MiyagiKpiValue["role"]) {
  const value = series.values.find((candidate) => candidate.role === role);
  return value?.status === "numeric" && typeof value.value === "number"
    ? value.value
    : null;
}

export const reviewedMiyagiPolicyHierarchy = hierarchy;
export const reviewedMiyagiPolicyDirections = hierarchy.directions;
export const reviewedMiyagiKpiGroups = [...reviewedGroups].sort(
  (left, right) => left.target_group_number - right.target_group_number,
);
export const miyagiKpiEvidencePackets = kpiEvidence;

export const miyagiKpiScopes = [
  {
    id: "pillar-1",
    label: "柱1",
    title: hierarchy.directions[0].title_original,
    groups: reviewedMiyagiKpiGroups.filter(
      (group) => group.scope_type === "pillar" && group.scope_number === 1,
    ),
  },
  ...hierarchy.directions[0].policies
    .flatMap((policy) => policy.measures)
    .slice(0, 5)
    .map((measure) => ({
      id: measure.id,
      label: `取組${measure.measure_number}`,
      title: measure.title_original,
      groups: reviewedMiyagiKpiGroups.filter(
        (group) =>
          group.scope_type === "measure" &&
          group.scope_number === measure.measure_number,
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
  implementationPeriod:
    `${hierarchy.implementation_period_start}〜${hierarchy.implementation_period_end}年度`,
  targetGroups: indicatorIndex.target_group_count,
  indicatorSeries: indicatorIndex.indicator_series_count,
  multiSeriesGroups: indicatorIndex.multi_series_group_count,
  additionalSeries: indicatorIndex.additional_series_count,
  sourcePages:
    indicatorIndex.source_pdf_page_end - indicatorIndex.source_pdf_page_start + 1,
  reviewedTargetGroups: reviewedGroups.length,
  reviewedIndicatorSeries: reviewedSeries.length,
  remainingTargetGroups: manifest.remaining_target_group_count,
  remainingIndicatorSeries: manifest.remaining_indicator_series_count,
  kpiEvidencePackets: kpiEvidence.length,
  lateTargetsNotSet: reviewedSeries.filter(
    (series) => series.values[3]?.status === "not_set",
  ).length,
  cumulativeGroups: reviewedGroups.filter(
    (group) => group.series[0]?.aggregation_scope === "cumulative_to_date",
  ).length,
  reviewedMultiSeriesGroups: reviewedGroups.filter(
    (group) => group.series.length > 1,
  ).length,
  missingUnitSeries: reviewedSeries.filter(
    (series) => series.unit_original === "単位記載なし",
  ).length,
  originalUnformattedTargets: reviewedSeries.filter((series) =>
    ["21400", "4126"].includes(
      series.values.find((value) => value.role === "midterm_target")
        ?.value_text_original ?? "",
    ),
  ).length,
  negativeValues: reviewedSeries.reduce(
    (total, series) =>
      total +
      series.values.filter(
        (value) => typeof value.value === "number" && value.value < 0,
      ).length,
    0,
  ),
  decliningMidtermGroups: reviewedGroups.filter((group) =>
    group.series.some((series) => {
      const current = numericValue(series, "current");
      const midtermTarget = numericValue(series, "midterm_target");
      return current !== null && midtermTarget !== null && midtermTarget < current;
    }),
  ).length,
  expectedKpiCount: manifest.expected_kpi_count,
  kpiCountStatus: manifest.kpi_count_status,
  activeWorkPackage: manifest.active_work_package,
  contentReviewStatus: indicatorIndex.content_review_status,
  kpiLinkageStatus: hierarchy.kpi_linkage_status,
};
