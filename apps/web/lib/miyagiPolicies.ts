import indicatorIndex from "../../../data/catalog/miyagi_indicator_source_index.json";
import sources from "../../../data/catalog/miyagi_policy_sources.json";
import manifest from "../../../data/catalog/miyagi_policy_review_manifest.json";
import measure1Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure1.json";
import measure2Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure2.json";
import measure3Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_measure3.json";
import pillar1Catalog from "../../../data/entities/policy/miyagi_kpi_catalog_pillar1.json";
import measure1Evidence from "../../../data/entities/policy/miyagi_kpi_measure1_evidence_packets.json";
import measure2Evidence from "../../../data/entities/policy/miyagi_kpi_measure2_evidence_packets.json";
import measure3aEvidence from "../../../data/entities/policy/miyagi_kpi_measure3a_evidence_packets.json";
import measure3bEvidence from "../../../data/entities/policy/miyagi_kpi_measure3b_evidence_packets.json";
import pillar1Evidence from "../../../data/entities/policy/miyagi_kpi_pillar1_evidence_packets.json";
import directionEvidence from "../../../data/entities/policy/miyagi_policy_direction_evidence_packets.json";
import hierarchy from "../../../data/entities/policy/miyagi_policy_hierarchy.json";

const policies = hierarchy.directions.flatMap((direction) => direction.policies);
const measures = policies.flatMap((policy) => policy.measures);
const reviewedGroups = [
  ...pillar1Catalog.items,
  ...measure1Catalog.items,
  ...measure2Catalog.items,
  ...measure3Catalog.items,
];
const reviewedSeries = reviewedGroups.flatMap((group) => group.series);
const kpiEvidence = [
  ...pillar1Evidence,
  ...measure1Evidence,
  ...measure2Evidence,
  ...measure3aEvidence,
  ...measure3bEvidence,
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
  decliningMidtermGroups: reviewedGroups.filter((group) => {
    const values = group.series[0]?.values;
    return values?.[1]?.value !== null
      && values?.[2]?.value !== null
      && values[2].value < values[1].value;
  }).length,
  expectedKpiCount: manifest.expected_kpi_count,
  kpiCountStatus: manifest.kpi_count_status,
  activeWorkPackage: manifest.active_work_package,
  contentReviewStatus: indicatorIndex.content_review_status,
};
