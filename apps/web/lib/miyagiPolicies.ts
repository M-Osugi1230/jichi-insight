import indicatorIndex from "../../../data/catalog/miyagi_indicator_source_index.json";
import sources from "../../../data/catalog/miyagi_policy_sources.json";
import manifest from "../../../data/catalog/miyagi_policy_review_manifest.json";
import measure1Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure1.json";
import measure2Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure2.json";
import measure3Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure3.json";
import measure4Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure4.json";
import measure5Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure5.json";
import measure6Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure6.json";
import measure7Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure7.json";
import measure8Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure8.json";
import measure9Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure9.json";
import measure10Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure10.json";
import measure11Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure11.json";
import measure12Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure12.json";
import measure13Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure13.json";
import measure14Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure14.json";
import measure15Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure15.json";
import pillar1Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_pillar1.json";
import pillar2Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_pillar2.json";
import pillar3Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_pillar3.json";
import pillar4Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_pillar4.json";
import measure1Evidence from "../../../data/entities/policy/miyagi_kpi_measure1_evidence_packets.json";
import measure2Evidence from "../../../data/entities/policy/miyagi_kpi_measure2_evidence_packets.json";
import measure3aEvidence from "../../../data/entities/policy/miyagi_kpi_measure3a_evidence_packets.json";
import measure3bEvidence from "../../../data/entities/policy/miyagi_kpi_measure3b_evidence_packets.json";
import measure4Evidence from "../../../data/entities/policy/miyagi_kpi_measure4_evidence_packets.json";
import measure5Evidence from "../../../data/entities/policy/miyagi_kpi_measure5_evidence_packets.json";
import measure6Evidence from "../../../data/entities/policy/miyagi_kpi_measure6_evidence_packets.json";
import measure7Evidence from "../../../data/entities/policy/miyagi_kpi_measure7_evidence_packets.json";
import measure8Evidence from "../../../data/entities/policy/miyagi_kpi_measure8_evidence_packets.json";
import measure9Evidence from "../../../data/entities/policy/miyagi_kpi_measure9_evidence_packets.json";
import measure10Evidence from "../../../data/entities/policy/miyagi_kpi_measure10_evidence_packets.json";
import measure11Evidence from "../../../data/entities/policy/miyagi_kpi_measure11_evidence_packets.json";
import measure12Evidence from "../../../data/entities/policy/miyagi_kpi_measure12_evidence_packets.json";
import measure13Evidence from "../../../data/entities/policy/miyagi_kpi_measure13_evidence_packets.json";
import measure14Evidence from "../../../data/entities/policy/miyagi_kpi_measure14_evidence_packets.json";
import measure15Evidence from "../../../data/entities/policy/miyagi_kpi_measure15_evidence_packets.json";
import pillar1Evidence from "../../../data/entities/policy/miyagi_kpi_pillar1_evidence_packets.json";
import pillar2Evidence from "../../../data/entities/policy/miyagi_kpi_pillar2_evidence_packets.json";
import pillar3Evidence from "../../../data/entities/policy/miyagi_kpi_pillar3_evidence_packets.json";
import pillar4Evidence from "../../../data/entities/policy/miyagi_kpi_pillar4_evidence_packets.json";
import directionEvidence from "../../../data/entities/policy/miyagi_policy_direction_evidence_packets.json";
import hierarchy from "../../../data/entities/policy/miyagi_policy_hierarchy.json";

export type MiyagiKpiValue = {
  role: "initial" | "current" | "midterm_target" | "late_target";
  period_original: "R1" | "R2" | "R3" | "R4" | "R5" | "R6" | "R7" | "R9" | "R12";
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
const directionOneMeasures = hierarchy.directions[0].policies.flatMap(
  (policy) => policy.measures,
);
const directionTwoMeasures = hierarchy.directions[1].policies.flatMap(
  (policy) => policy.measures,
);
const directionThreeMeasures = hierarchy.directions[2].policies.flatMap(
  (policy) => policy.measures,
);
const directionFourMeasures = hierarchy.directions[3].policies.flatMap(
  (policy) => policy.measures,
);

const reviewedGroups = [
  ...pillar1Catalog.items,
  ...measure1Catalog.items,
  ...measure2Catalog.items,
  ...measure3Catalog.items,
  ...measure4Catalog.items,
  ...measure5Catalog.items,
  ...pillar2Catalog.items,
  ...measure6Catalog.items,
  ...measure7Catalog.items,
  ...measure8Catalog.items,
  ...measure9Catalog.items,
  ...pillar3Catalog.items,
  ...measure10Catalog.items,
  ...measure11Catalog.items,
  ...measure12Catalog.items,
  ...measure13Catalog.items,
  ...measure14Catalog.items,
  ...pillar4Catalog.items,
  ...measure15Catalog.items,
] as MiyagiKpiGroup[];
const reviewedSeries = reviewedGroups.flatMap((group) => group.series);
const kpiEvidence = [
  ...pillar1Evidence,
  ...measure1Evidence,
  ...measure2Evidence,
  ...measure3aEvidence,
  ...measure3bEvidence,
  ...measure4Evidence,
  ...measure5Evidence,
  ...pillar2Evidence,
  ...measure6Evidence,
  ...measure7Evidence,
  ...measure8Evidence,
  ...measure9Evidence,
  ...pillar3Evidence,
  ...measure10Evidence,
  ...measure11Evidence,
  ...measure12Evidence,
  ...measure13Evidence,
  ...measure14Evidence,
  ...pillar4Evidence,
  ...measure15Evidence,
];

export const reviewedMiyagiPolicyHierarchy = hierarchy;
export const reviewedMiyagiPolicyDirections = hierarchy.directions;
export const reviewedMiyagiKpiGroups = [...reviewedGroups].sort(
  (left, right) => left.target_group_number - right.target_group_number,
);
export const miyagiKpiEvidencePackets = kpiEvidence;

const scopeForMeasure = (measure: (typeof measures)[number]) => ({
  id: measure.id,
  label: `取組${measure.measure_number}`,
  title: measure.title_original,
  groups: reviewedMiyagiKpiGroups.filter(
    (group) => group.scope_type === "measure" && group.scope_number === measure.measure_number,
  ),
});

export const miyagiKpiScopes = [
  {
    id: "pillar-1",
    label: "柱1",
    title: hierarchy.directions[0].title_original,
    groups: reviewedMiyagiKpiGroups.filter(
      (group) => group.scope_type === "pillar" && group.scope_number === 1,
    ),
  },
  ...directionOneMeasures.slice(0, 5).map(scopeForMeasure),
  {
    id: "pillar-2",
    label: "柱2",
    title: hierarchy.directions[1].title_original,
    groups: reviewedMiyagiKpiGroups.filter(
      (group) => group.scope_type === "pillar" && group.scope_number === 2,
    ),
  },
  ...directionTwoMeasures.slice(0, 4).map(scopeForMeasure),
  {
    id: "pillar-3",
    label: "柱3",
    title: hierarchy.directions[2].title_original,
    groups: reviewedMiyagiKpiGroups.filter(
      (group) => group.scope_type === "pillar" && group.scope_number === 3,
    ),
  },
  ...directionThreeMeasures.slice(0, 5).map(scopeForMeasure),
  {
    id: "pillar-4",
    label: "柱4",
    title: hierarchy.directions[3].title_original,
    groups: reviewedMiyagiKpiGroups.filter(
      (group) => group.scope_type === "pillar" && group.scope_number === 4,
    ),
  },
  ...directionFourMeasures.slice(0, 1).map(scopeForMeasure),
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
  negativeValues: reviewedSeries.reduce(
    (total, series) =>
      total + series.values.filter((value) => value.value !== null && value.value < 0).length,
    0,
  ),
  decliningMidtermGroups: reviewedGroups.filter((group) =>
    group.series.some((series) => {
      const current = series.values[1]?.value;
      const target = series.values[2]?.value;
      return current !== null && target !== null && target < current;
    }),
  ).length,
  expectedKpiCount: manifest.expected_kpi_count,
  kpiCountStatus: manifest.kpi_count_status,
  activeWorkPackage: manifest.active_work_package,
  contentReviewStatus: indicatorIndex.content_review_status,
};
