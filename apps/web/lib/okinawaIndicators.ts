import manifest from "../../../data/catalog/okinawa_midterm_indicator_review_manifest.json";
import majorIndicators from "../../../data/reviewed/okinawa_midterm_major_indicators.json";
import outcomePart1 from "../../../data/reviewed/okinawa_midterm_outcome_indicators_part1.json";
import outcomePart2 from "../../../data/reviewed/okinawa_midterm_outcome_indicators_part2.json";
import outcomePart3 from "../../../data/reviewed/okinawa_midterm_outcome_indicators_part3.json";

type RawIndicator = {
  id: string;
  evidence_id: string;
  indicator_level: "major" | "outcome";
  sequence: number;
  policy_code_original: string;
  policy_title_original: string;
  indicator_name_original: string;
  baseline_original: string;
  target_r9_original: string;
  national_current_original: string;
  rationale_source_original: string;
  island_indicator_original: string | null;
  sdgs_priority_original: string | null;
  is_island_indicator: boolean;
  has_sdgs_priority: boolean;
  target_value_kind: "numeric_or_mixed" | "qualitative";
  national_comparison_status: "provided" | "unavailable";
  source_value_note: string | null;
  source_pdf_page: number;
  source_table_row: number;
  review_status: "reviewed";
  policy_achievement_assessment_status: "not_assessed";
};

export type OkinawaIndicator = {
  id: string;
  evidenceId: string;
  level: "major" | "outcome";
  sequence: number;
  policyCode: string;
  policyTitle: string;
  name: string;
  baseline: string;
  targetR9: string;
  nationalCurrent: string;
  rationaleSource: string;
  islandIndicator: boolean;
  sdgsPriority: string | null;
  qualitativeTarget: boolean;
  nationalComparisonProvided: boolean;
  sourceValueNote: string | null;
  sourceUrl: string;
  sourcePage: number;
  sourceRow: number;
};

function compactOriginal(value: string) {
  return value
    .replace(/(?<=[ぁ-んァ-ヶ一-龯々ー])\s+(?=[ぁ-んァ-ヶ一-龯々ー])/gu, "")
    .replace(/\s+/gu, " ")
    .trim();
}

function toIndicator(record: RawIndicator): OkinawaIndicator {
  return {
    id: record.id,
    evidenceId: record.evidence_id,
    level: record.indicator_level,
    sequence: record.sequence,
    policyCode: record.policy_code_original,
    policyTitle: compactOriginal(record.policy_title_original),
    name: compactOriginal(record.indicator_name_original),
    baseline: compactOriginal(record.baseline_original),
    targetR9: compactOriginal(record.target_r9_original),
    nationalCurrent: compactOriginal(record.national_current_original),
    rationaleSource: compactOriginal(record.rationale_source_original),
    islandIndicator: record.is_island_indicator,
    sdgsPriority: record.sdgs_priority_original
      ? compactOriginal(record.sdgs_priority_original)
      : null,
    qualitativeTarget: record.target_value_kind === "qualitative",
    nationalComparisonProvided: record.national_comparison_status === "provided",
    sourceValueNote: record.source_value_note,
    sourceUrl: manifest.source_url,
    sourcePage: record.source_pdf_page,
    sourceRow: record.source_table_row,
  };
}

const rawRecords = [
  ...majorIndicators.records,
  ...outcomePart1.records,
  ...outcomePart2.records,
  ...outcomePart3.records,
] as RawIndicator[];

export const reviewedOkinawaIndicators = rawRecords.map(toIndicator);

export const okinawaIndicatorStats = {
  reviewedIndicators: manifest.reviewed_indicator_count,
  majorIndicators: manifest.major_indicator_count,
  outcomeIndicators: manifest.outcome_indicator_count,
  evidencePackets: manifest.evidence_packet_count,
  islandIndicators: manifest.island_indicator_count,
  sdgsPriorityIndicators: manifest.sdgs_priority_indicator_count,
  qualitativeTargets: manifest.qualitative_target_count,
  nationalComparisons: manifest.national_comparison_provided_count,
  sourceValueNotes: manifest.source_value_note_count,
  assessedIndicators: manifest.policy_achievement_assessed_indicator_count,
};

export const okinawaReviewManifest = manifest;
