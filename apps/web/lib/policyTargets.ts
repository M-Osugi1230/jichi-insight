import targetEvidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_01_target_evidence_packet.json";
import targetCatalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_01_targets.json";

export type PolicyTargetComponent = {
  label: string | null;
  baseline_value: number;
  baseline_unit: string;
  baseline_period: string;
  baseline_scope: "snapshot" | "annual" | "cumulative";
  target_value: number;
  target_unit: string;
  target_period: string;
  target_scope: "snapshot" | "annual" | "five_year_cumulative" | "cumulative";
  preferred_direction: "increase" | "decrease";
};

export type PolicyTarget = {
  id: string;
  target_number: number;
  submeasure_title_original: string;
  indicator_name_original: string;
  components: PolicyTargetComponent[];
  actual_linkage_status: "not_linked" | "partial" | "linked";
  evaluation_status: "not_assessed" | "partially_assessed" | "assessed";
};

export type PolicyTargetCatalog = {
  id: string;
  policy_initiative_id: string;
  source_ids: string[];
  source_document_url: string;
  source_page: number;
  printed_page: number;
  items: PolicyTarget[];
  reviewed_at: string;
  review_status: "reviewed" | "verified";
  confidence: "high" | "medium" | "low" | "not_assessable";
};

export type PolicyTargetEvidence = {
  id: string;
  subject_type: "policy_target_catalog";
  subject_id: string;
  claims: Array<{
    field: string;
    statement: string;
    source_ids: string[];
    location_note: string | null;
    decision: "accepted" | "rejected" | "needs_review" | "not_assessable";
    review_note: string | null;
  }>;
  open_questions: string[];
  review_status: "reviewed" | "verified";
};

export const initiative01TargetCatalog = targetCatalog as PolicyTargetCatalog;
export const initiative01TargetEvidence = targetEvidence as PolicyTargetEvidence;

export const initiative01TargetStats = {
  reviewedTargets: initiative01TargetCatalog.items.length,
  actualsLinked: initiative01TargetCatalog.items.filter(
    (target) => target.actual_linkage_status !== "not_linked",
  ).length,
  assessed: initiative01TargetCatalog.items.filter(
    (target) => target.evaluation_status !== "not_assessed",
  ).length,
};

export function formatTargetValue(value: number, unit: string) {
  return `${value.toLocaleString("ja-JP")}${unit}`;
}

export function targetScopeLabel(
  scope:
    | PolicyTargetComponent["baseline_scope"]
    | PolicyTargetComponent["target_scope"],
) {
  const labels = {
    snapshot: "時点値",
    annual: "年次値",
    cumulative: "累計値",
    five_year_cumulative: "5年間累計",
  } as const;
  return labels[scope];
}
