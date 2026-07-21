import reviewManifest from "../../../data/catalog/tokyo_policy_target_review_manifest.json";
import policySources from "../../../data/catalog/tokyo_policy_sources.json";
import cardEvidencePackets from "../../../data/evidence/tokyo_policy_target_card_evidence.json";
import targetCardCatalog from "../../../data/reviewed/tokyo_policy_target_cards.json";
import detailedEvidencePackets from "../../../data/entities/policy/tokyo_policy_target_children_evidence_packets.json";
import detailedTargetCatalog from "../../../data/entities/policy/tokyo_policy_target_catalog_children.json";

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

export type TokyoPolicyArea = {
  code: string;
  name_original: string;
  page_start: number;
  page_end: number;
  target_card_count: number;
  policy_measure_count: number;
};

export type TokyoPolicyTargetSemanticFlag =
  | "cumulative"
  | "maintenance"
  | "minimum"
  | "maximum"
  | "ranking"
  | "qualitative"
  | "rate"
  | "count"
  | "distance_area_volume"
  | "money"
  | "time";

export type TokyoPolicyTargetCard = {
  id: string;
  display_order: number;
  policy_area_code: string;
  policy_area_name_original: string;
  policy_measure_original: string | null;
  target_name_original: string;
  source_page: number;
  source_card_bbox: [number, number, number, number];
  highlighted_target_text_original: string[];
  periods_original: string[];
  units_original: string[];
  semantic_flags: TokyoPolicyTargetSemanticFlag[];
  source_card_text_original: string;
  detailed_series_status: "reviewed" | "not_normalized";
  actual_linkage_status: "not_linked";
  evaluation_status: "not_assessed";
  review_status: "reviewed";
  confidence: "high";
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

export const reviewedTokyoPolicyTargetCards =
  targetCardCatalog.items as TokyoPolicyTargetCard[];
export const reviewedTokyoPolicyAreas =
  targetCardCatalog.policy_areas as TokyoPolicyArea[];
export const reviewedTokyoPolicyTargets =
  detailedTargetCatalog.items as TokyoPolicyTarget[];
export const tokyoPolicySources = policySources.records as TokyoPolicySource[];
export const tokyoPolicyTargetCardEvidencePackets = cardEvidencePackets;
export const tokyoPolicyTargetEvidencePackets = detailedEvidencePackets;
export const tokyoPolicyTargetReviewManifest = reviewManifest;

export const tokyoPolicyTargetStats = {
  reviewedTargetGroups: reviewManifest.reviewed_target_group_count,
  reviewedTargetCards: reviewManifest.reviewed_target_card_count,
  policyAreas: reviewManifest.reviewed_policy_area_count,
  evidencePackets: reviewManifest.card_evidence_packet_count,
  detailedTargetGroups: reviewManifest.detailed_reviewed_target_group_count,
  reviewedSeries: reviewManifest.detailed_reviewed_indicator_series_count,
  detailedEvidencePackets: reviewManifest.detailed_evidence_packet_count,
  reviewedPages: reviewManifest.reviewed_page_count,
  sourcePages: reviewManifest.source_page_count,
  remainingPages: reviewManifest.remaining_page_count,
  actualLinkedSeries: reviewManifest.actual_linked_indicator_series_count,
  assessedTargetGroups: reviewManifest.evaluation_assessed_target_group_count,
  nextReviewScope: reviewManifest.next_review_scope,
};

export const tokyoSemanticFlagLabels: Record<
  TokyoPolicyTargetSemanticFlag,
  string
> = {
  cumulative: "累計",
  maintenance: "維持",
  minimum: "下限",
  maximum: "上限",
  ranking: "順位",
  qualitative: "定性",
  rate: "割合",
  count: "件数・人数",
  distance_area_volume: "距離・面積・容量",
  money: "金額",
  time: "時間",
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
