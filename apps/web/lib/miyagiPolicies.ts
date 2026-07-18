import sources from "../../../data/catalog/miyagi_policy_sources.json";
import manifest from "../../../data/catalog/miyagi_policy_review_manifest.json";
import evidence from "../../../data/entities/policy/miyagi_policy_direction_evidence_packets.json";
import hierarchy from "../../../data/entities/policy/miyagi_policy_hierarchy.json";

const policies = hierarchy.directions.flatMap((direction) => direction.policies);
const measures = policies.flatMap((policy) => policy.measures);

export const miyagiPolicyReviewStats = {
  sources: sources.records.length,
  reviewedSources: sources.records.filter(
    (source) => source.review_status === "reviewed",
  ).length,
  directions: hierarchy.directions.length,
  policies: policies.length,
  measures: measures.length,
  recoveryAreas: hierarchy.recovery_support_areas.length,
  evidencePackets: evidence.length,
  implementationPeriod:
    `${hierarchy.implementation_period_start}〜${hierarchy.implementation_period_end}年度`,
  expectedKpiCount: manifest.expected_kpi_count,
  kpiCountStatus: manifest.kpi_count_status,
  activeWorkPackage: manifest.active_work_package,
};
