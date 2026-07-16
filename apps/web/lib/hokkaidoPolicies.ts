import hokkaidoDirectionEvidence from "../../../data/entities/policy/hokkaido_policy_direction_evidence_packets.json";
import hokkaidoHierarchy from "../../../data/entities/policy/hokkaido_policy_hierarchy.json";

export type HokkaidoPolicyField = {
  id: string;
  display_order: number;
  title_original: string;
};

export type HokkaidoPolicyDirection = {
  id: string;
  display_order: number;
  title_original: string;
  fields: HokkaidoPolicyField[];
};

export type HokkaidoPolicyHierarchy = {
  id: string;
  prefecture_code: string;
  municipality_key: string;
  plan_source_ids: string[];
  plan_title_original: string;
  plan_period_start: number;
  plan_period_end: number | null;
  plan_period_original: string;
  directions: HokkaidoPolicyDirection[];
  progress_linkage_status: "not_linked" | "partial" | "linked";
  evaluation_status: "not_assessed" | "partially_assessed" | "assessed";
  source_location: string;
  reviewed_at: string;
  review_status: "reviewed" | "verified";
  confidence: "high" | "medium" | "low" | "not_assessable";
};

export const reviewedHokkaidoPolicyHierarchy =
  hokkaidoHierarchy as HokkaidoPolicyHierarchy;

export const reviewedHokkaidoPolicyDirections = [
  ...reviewedHokkaidoPolicyHierarchy.directions,
].sort((left, right) => left.display_order - right.display_order);

export const reviewedHokkaidoPolicyFields = reviewedHokkaidoPolicyDirections.flatMap(
  (direction) =>
    [...direction.fields].sort(
      (left, right) => left.display_order - right.display_order,
    ),
);

export const hokkaidoPolicyDirectionEvidence = hokkaidoDirectionEvidence;

export const hokkaidoPolicyHierarchyStats = {
  reviewedDirections: reviewedHokkaidoPolicyDirections.length,
  reviewedFields: reviewedHokkaidoPolicyFields.length,
  evidencePackets: hokkaidoPolicyDirectionEvidence.length,
  indicatorTarget: 108,
  duplicateInclusiveIndicatorRows: 113,
  progressLinked:
    reviewedHokkaidoPolicyHierarchy.progress_linkage_status === "linked" ? 1 : 0,
  assessed:
    reviewedHokkaidoPolicyHierarchy.evaluation_status === "assessed" ? 1 : 0,
};
