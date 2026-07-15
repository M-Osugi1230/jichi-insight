import policyDirectionEvidence from "../../../data/entities/policy/fukuoka_prefecture_policy_direction_evidence_packets.json";
import policyDirections from "../../../data/entities/policy/fukuoka_prefecture_policy_directions.json";

import { policySources, type PolicySourceRecord } from "./policySources";

export type PolicyDirection = {
  id: string;
  municipality_id: string;
  plan_source_ids: string[];
  display_order: number;
  title_original: string;
  plan_period_start: number;
  plan_period_end: number;
  level: "strategic_direction";
  progress_linkage_status: "not_linked" | "partial" | "linked";
  evaluation_status: "not_assessed" | "partially_assessed" | "assessed";
  source_location: string;
  reviewed_at: string;
  review_status: "reviewed" | "verified";
  confidence: "high" | "medium" | "low" | "not_assessable";
};

export type PolicyDirectionEvidence = {
  id: string;
  subject_type: "policy_direction";
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

export const fukuokaPolicyDirections = [...(policyDirections as PolicyDirection[])].sort(
  (left, right) => left.display_order - right.display_order,
);

export const fukuokaPolicyDirectionEvidence =
  policyDirectionEvidence as PolicyDirectionEvidence[];

export function evidenceForPolicyDirection(direction: PolicyDirection) {
  return fukuokaPolicyDirectionEvidence.find(
    (packet) => packet.subject_id === direction.id,
  );
}

export function sourcesForPolicyDirection(direction: PolicyDirection): PolicySourceRecord[] {
  return policySources.filter((source) => direction.plan_source_ids.includes(source.id));
}

export const policyDirectionStats = {
  reviewedDirections: fukuokaPolicyDirections.length,
  progressLinked: fukuokaPolicyDirections.filter(
    (direction) => direction.progress_linkage_status === "linked",
  ).length,
  assessed: fukuokaPolicyDirections.filter(
    (direction) => direction.evaluation_status === "assessed",
  ).length,
};
