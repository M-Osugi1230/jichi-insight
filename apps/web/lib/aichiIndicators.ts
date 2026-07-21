import indicatorCatalog from "../../../data/reviewed/aichi_policy_indicators.json";
import reviewManifest from "../../../data/catalog/aichi_policy_indicator_review_manifest.json";
import policySources from "../../../data/catalog/aichi_policy_sources.json";

export type AichiIndicatorValue = {
  role: "baseline" | "current" | "target";
  period: string;
  value: number | string | null;
  value_text_original: string;
  status: "numeric" | "numeric_text" | "qualitative" | "missing";
  operator: "exact" | "minimum" | "maximum" | "approximate";
  aggregation_scope: "single_period" | "cumulative" | "multi_period_average";
};

export type AichiIndicatorSeries = {
  label: string | null;
  unit_original: string;
  direction: string;
  values: AichiIndicatorValue[];
  comparability_note_original: string;
};

export type AichiPolicyIndicator = {
  id: string;
  display_order: number;
  policy_direction_code: string;
  policy_direction_name_original: string;
  indicator_name_original: string;
  source_page: number;
  repost_of: string | null;
  series: AichiIndicatorSeries[];
  linked_current_series_count: number;
  target_series_count: number;
  target_revision_status: "unchanged_or_not_applicable" | "revised_in_2025_report";
  review_status: "reviewed";
  evaluation_status: "not_assessed";
  quality_note: string;
};

export type AichiPolicyDirection = {
  code: string;
  name_original: string;
  indicator_row_count: number;
  indicator_series_count: number;
};

export type AichiPolicySource = {
  id: string;
  category: string;
  title: string;
  url: string;
  publication_date: string;
  review_status: string;
  role_note: string;
};

export const reviewedAichiPolicyIndicators =
  indicatorCatalog.items as AichiPolicyIndicator[];
export const reviewedAichiPolicyDirections =
  indicatorCatalog.policy_directions as AichiPolicyDirection[];
export const aichiPolicySources = policySources.records as AichiPolicySource[];
export const aichiPolicyIndicatorReviewManifest = reviewManifest;

export const aichiPolicyIndicatorStats = {
  policyDirections: reviewManifest.policy_direction_count,
  indicatorRows: reviewManifest.reviewed_indicator_row_count,
  uniqueIndicators: reviewManifest.unique_indicator_count,
  indicatorSeries: reviewManifest.reviewed_indicator_series_count,
  evidencePackets: reviewManifest.evidence_packet_count,
  currentLinkedSeries: reviewManifest.series_with_current_value,
  targetSeries: reviewManifest.series_with_target_value,
  repostIndicators: reviewManifest.repost_indicator_count,
  targetRevisionEvents: reviewManifest.target_revision_event_count,
  managementProjects: reviewManifest.management_projects_evaluated_2025,
  managementProjectsWithoutResult:
    reviewManifest.management_projects_without_evaluation_result_2025,
  policyAssessments: reviewManifest.policy_achievement_assessed_indicator_count,
  nextReviewScope: reviewManifest.next_review_scope,
};

export const aichiValueRoleLabels: Record<AichiIndicatorValue["role"], string> = {
  baseline: "策定時",
  current: "現状",
  target: "進捗目標",
};
