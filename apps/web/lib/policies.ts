import policyDirectionEvidence from "../../../data/entities/policy/fukuoka_prefecture_policy_direction_evidence_packets.json";
import policyDirections from "../../../data/entities/policy/fukuoka_prefecture_policy_directions.json";
import policyInitiativeCatalog from "../../../data/entities/policy/fukuoka_prefecture_policy_initiatives.json";

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

export type PolicyInitiative = {
  id: string;
  policy_direction_id: string;
  sequence_number: number;
  title_original: string;
  plan_page_start: number;
  source_page: number;
  progress_linkage_status: "not_linked" | "partial" | "linked";
  evaluation_status: "not_assessed" | "partially_assessed" | "assessed";
};

export type PolicyInitiativeCatalog = {
  id: string;
  municipality_id: string;
  plan_period_start: number;
  plan_period_end: number;
  plan_source_ids: string[];
  source_document_url: string;
  progress_source_ids: string[];
  items: PolicyInitiative[];
  reviewed_at: string;
  review_status: "reviewed" | "verified";
  confidence: "high" | "medium" | "low" | "not_assessable";
};

export const fukuokaPolicyDirections = [...(policyDirections as PolicyDirection[])].sort(
  (left, right) => left.display_order - right.display_order,
);

export const fukuokaPolicyDirectionEvidence =
  policyDirectionEvidence as PolicyDirectionEvidence[];

export const fukuokaPolicyInitiativeCatalog =
  policyInitiativeCatalog as PolicyInitiativeCatalog;

export const fukuokaPolicyInitiatives = [...fukuokaPolicyInitiativeCatalog.items].sort(
  (left, right) => left.sequence_number - right.sequence_number,
);

export function evidenceForPolicyDirection(direction: PolicyDirection) {
  return fukuokaPolicyDirectionEvidence.find(
    (packet) => packet.subject_id === direction.id,
  );
}

export function sourcesForPolicyDirection(direction: PolicyDirection): PolicySourceRecord[] {
  return policySources.filter((source) => direction.plan_source_ids.includes(source.id));
}

export function initiativesForPolicyDirection(direction: PolicyDirection) {
  return fukuokaPolicyInitiatives.filter(
    (initiative) => initiative.policy_direction_id === direction.id,
  );
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

export const policyInitiativeStats = {
  reviewedInitiatives: fukuokaPolicyInitiatives.length,
  progressLinked: fukuokaPolicyInitiatives.filter(
    (initiative) => initiative.progress_linkage_status === "linked",
  ).length,
  assessed: fukuokaPolicyInitiatives.filter(
    (initiative) => initiative.evaluation_status === "assessed",
  ).length,
};
