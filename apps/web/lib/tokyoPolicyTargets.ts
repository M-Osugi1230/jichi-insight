import evidencePackets from "../../../data/entities/policy/tokyo_policy_target_children_evidence_packets.json";
import targetCatalog from "../../../data/entities/policy/tokyo_policy_target_catalog_children.json";
import reviewManifest from "../../../data/catalog/tokyo_policy_target_review_manifest.json";
import policySources from "../../../data/catalog/tokyo_policy_sources.json";

export type TokyoPolicyTargetValue = {
  role: "baseline" | "current" | "actual" | "intermediate_target" | "final_target";
  period: string;
  value: number | string | null;
  status: "numeric" | "qualitative" | "missing" | "conditional";
  operator: "exact" | "minimum" | "maximum" | "maintain";
  aggregation_scope: "single_period" | "snapshot" | "cumulative";
  value_text_original: string | null;
};

export type TokyoPolicyTargetSeries = {
  id: string;
  label: string | null;
  unit_original: string;
  temporal_scope: "calendar_year" | "fiscal_year" | "snapshot";
  direction: "increase" | "decrease" | "maintain" | "increase_then_maintain";
  values: TokyoPolicyTargetValue[];
};

export type TokyoPolicyTarget = {
  id: string;
  target_group_number: number;
  target_name_original: string;
  policy_measure_original: string;
  source_page: number;
  population_scope_original: string | null;
  series: TokyoPolicyTargetSeries[];
  comparability_note_original: string;
  actual_linkage_status: "not_linked";
  evaluation_status: "not_assessed";
  review_status: "reviewed";
  confidence: "high" | "medium" | "low";
};

export type TokyoPolicySource = {
  id: string;
  category: string;
  title: string;
  url: string;
  publication_date: string;
  review_status: string;
  role_note: string;
};

export const reviewedTokyoPolicyTargets = targetCatalog.items as TokyoPolicyTarget[];
export const tokyoPolicySources = policySources.records as TokyoPolicySource[];
export const tokyoPolicyTargetEvidencePackets = evidencePackets;
export const tokyoPolicyTargetReviewManifest = reviewManifest;

export const tokyoPolicyTargetStats = {
  reviewedTargetGroups: reviewManifest.reviewed_target_group_count,
  reviewedSeries: reviewManifest.reviewed_indicator_series_count,
  evidencePackets: reviewManifest.evidence_packet_count,
  reviewedPages: reviewManifest.reviewed_page_count,
  sourcePages: reviewManifest.source_page_count,
  remainingPages: reviewManifest.remaining_page_count,
  actualLinkedSeries: reviewManifest.actual_linked_indicator_series_count,
  assessedTargetGroups: reviewManifest.evaluation_assessed_target_group_count,
  nextReviewScope: reviewManifest.next_review_scope,
};

export function tokyoValueRoleLabel(role: TokyoPolicyTargetValue["role"]) {
  const labels: Record<TokyoPolicyTargetValue["role"], string> = {
    baseline: "基準値",
    current: "現状値",
    actual: "実績",
    intermediate_target: "途中目標",
    final_target: "最終目標",
  };
  return labels[role];
}

export function tokyoValueDisplay(value: TokyoPolicyTargetValue, unit: string) {
  if (value.value_text_original === null) return "未公表";
  if (unit === "実施状態") return value.value_text_original;
  return `${value.value_text_original}${unit}`;
}
