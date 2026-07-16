import indicatorCompositeTargets from "../../../data/catalog/miyagi_indicator_composite_targets.json";
import indicatorSourceIndex from "../../../data/catalog/miyagi_indicator_source_index.json";
import sourceInventory from "../../../data/catalog/miyagi_policy_source_inventory.json";
import hierarchy from "../../../data/entities/policy/miyagi_policy_hierarchy.json";
import hierarchyEvidence from "../../../data/entities/policy/miyagi_policy_hierarchy_evidence_packets.json";

export type MiyagiMeasure = {
  id: string;
  measure_number: number;
  display_order: number;
  title_original: string;
};

export type MiyagiPolicy = {
  id: string;
  policy_number: number;
  display_order: number;
  title_original: string;
  measures: MiyagiMeasure[];
};

export type MiyagiDirection = {
  id: string;
  display_order: number;
  title_original: string;
  policies: MiyagiPolicy[];
};

export type MiyagiParallelDomain = {
  id: string;
  display_order: number;
  title_original: string;
  relationship_note: string;
};

export const reviewedMiyagiPolicyHierarchy = hierarchy;
export const reviewedMiyagiPolicyDirections = hierarchy.directions as MiyagiDirection[];
export const reviewedMiyagiParallelDomains = hierarchy.parallel_domains as MiyagiParallelDomain[];
export const miyagiPolicySourceInventory = sourceInventory;
export const miyagiPolicyHierarchyEvidencePackets = hierarchyEvidence;
export const miyagiIndicatorSourceIndex = indicatorSourceIndex;
export const miyagiIndicatorCompositeTargets = indicatorCompositeTargets;

const policies = reviewedMiyagiPolicyDirections.flatMap(
  (direction) => direction.policies,
);
const measures = policies.flatMap((policy) => policy.measures);

export const miyagiPolicyHierarchyStats = {
  directions: reviewedMiyagiPolicyDirections.length,
  policies: policies.length,
  measures: measures.length,
  parallelDomains: reviewedMiyagiParallelDomains.length,
  evidencePackets: hierarchyEvidence.length,
  inventorySources: sourceInventory.sources.length,
  inventoryRelationships: sourceInventory.relationships.length,
  indexedTargets: indicatorSourceIndex.unique_target_count,
  indexedDisplayRows: indicatorSourceIndex.display_row_count,
  indexedSections: indicatorSourceIndex.sections.length,
  compositeTargets: indicatorCompositeTargets.target_count,
  additionalSeriesRows: indicatorCompositeTargets.additional_series_row_count,
};
