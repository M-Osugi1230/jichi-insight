import part1 from "../../../data/reviewed/hiroshima_revised_vision_indicators_part1.json";
import part2 from "../../../data/reviewed/hiroshima_revised_vision_indicators_part2.json";
import part3 from "../../../data/reviewed/hiroshima_revised_vision_indicators_part3.json";
import manifest from "../../../data/catalog/hiroshima_revised_vision_indicator_review_manifest.json";

export type HiroshimaIndicator = {
  id: string;
  evidence_id: string;
  area: string;
  name: string;
  baseline: string;
  current: string;
  target: string;
  target_period: string;
  change: string;
  source: string;
  page: number;
  review: "reviewed";
  assessment: "not_assessed";
};

export const reviewedHiroshimaIndicators = [
  ...part1.records,
  ...part2.records,
  ...part3.records,
] as HiroshimaIndicator[];

export const hiroshimaIndicatorAreas = Array.from(
  new Set(reviewedHiroshimaIndicators.map((indicator) => indicator.area)),
);

export const hiroshimaIndicatorStats = {
  policyAreas: manifest.policy_area_count,
  reviewedIndicators: manifest.reviewed_indicator_count,
  evidencePackets: manifest.evidence_packet_count,
  currentValues: manifest.indicators_with_numeric_or_qualitative_current_value_count,
  pendingMeasurements: manifest.pending_measurement_indicator_count,
  qualitativeTargets: manifest.qualitative_target_indicator_count,
  assessedIndicators: manifest.policy_achievement_assessed_indicator_count,
};

export const hiroshimaReviewManifest = manifest;
