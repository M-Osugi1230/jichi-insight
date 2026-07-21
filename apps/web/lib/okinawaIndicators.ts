import part1 from "../../../data/reviewed/okinawa_midterm_indicators_part1.json";
import part2 from "../../../data/reviewed/okinawa_midterm_indicators_part2.json";
import part3 from "../../../data/reviewed/okinawa_midterm_indicators_part3.json";
import part4 from "../../../data/reviewed/okinawa_midterm_indicators_part4.json";
import manifest from "../../../data/catalog/okinawa_midterm_indicator_review_manifest.json";

export type OkinawaIndicatorLayer = "major" | "outcome";

export type OkinawaIndicator = {
  display_order: number;
  indicator_id: string;
  evidence_id: string;
  indicator_layer: OkinawaIndicatorLayer;
  policy_original: string;
  indicator_name_original: string;
  baseline_original: string;
  target_r9_original: string;
  national_current_original: string | null;
  rationale_and_source_original: string;
  remote_island_marker_original: string | null;
  sdgs_priority_original: string | null;
  source_pdf_page: number;
  source_table_row: number;
  review_status: "reviewed";
  policy_achievement_assessment_status: "not_assessed";
};

export const reviewedOkinawaIndicators = [
  ...part1.records,
  ...part2.records,
  ...part3.records,
  ...part4.records,
] as OkinawaIndicator[];

export function compactOkinawaText(value: string | null) {
  if (!value) return "－";
  return value
    .replace(/(?<=[ぁ-んァ-ヶ一-龯々ー])\s+(?=[ぁ-んァ-ヶ一-龯々ー])/gu, "")
    .replace(/\s+/gu, " ")
    .trim();
}

export function hasOkinawaNationalComparator(indicator: OkinawaIndicator) {
  return ![null, "－", "-"].includes(indicator.national_current_original);
}

export function isOkinawaQualitativeTarget(indicator: OkinawaIndicator) {
  return !/[0-9０-９]/u.test(indicator.target_r9_original);
}

export const okinawaIndicatorStats = {
  reviewedIndicators: manifest.reviewed_indicator_count,
  majorIndicators: manifest.major_indicator_count,
  outcomeIndicators: manifest.outcome_indicator_count,
  evidencePackets: manifest.evidence_packet_count,
  nationalComparators: manifest.national_comparator_present_count,
  remoteIslandIndicators: manifest.remote_island_indicator_count,
  sdgsLinkedIndicators: manifest.sdgs_linked_indicator_count,
  qualitativeTargets: manifest.qualitative_target_count,
  activityIndicators: manifest.activity_indicator_included_count,
  assessedIndicators: manifest.policy_achievement_assessed_indicator_count,
};

export const okinawaReviewManifest = manifest;
