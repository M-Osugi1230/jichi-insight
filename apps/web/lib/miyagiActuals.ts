import measure1Evidence from "../../../data/entities/policy/miyagi_kpi_actuals_measure1_2024_evidence_packets.json";
import measure1Actuals from "../../../data/entities/policy/miyagi_kpi_actuals_measure1_2024.json";
import measure2Evidence from "../../../data/entities/policy/miyagi_kpi_actuals_measure2_2024_evidence_packets.json";
import measure2Actuals from "../../../data/entities/policy/miyagi_kpi_actuals_measure2_2024.json";
import measure3Evidence from "../../../data/entities/policy/miyagi_kpi_actuals_measure3_2024_evidence_packets.json";
import measure3Actuals from "../../../data/entities/policy/miyagi_kpi_actuals_measure3_2024.json";
import measure4Evidence from "../../../data/entities/policy/miyagi_kpi_actuals_measure4_2024_evidence_packets.json";
import measure4Actuals from "../../../data/entities/policy/miyagi_kpi_actuals_measure4_2024.json";
import measure5Evidence from "../../../data/entities/policy/miyagi_kpi_actuals_measure5_2024_evidence_packets.json";
import measure5Actuals from "../../../data/entities/policy/miyagi_kpi_actuals_measure5_2024.json";
import measure6Evidence from "../../../data/entities/policy/miyagi_kpi_actuals_measure6_2024_evidence_packets.json";
import measure6Actuals from "../../../data/entities/policy/miyagi_kpi_actuals_measure6_2024.json";
import measure7Evidence from "../../../data/entities/policy/miyagi_kpi_actuals_measure7_2024_evidence_packets.json";
import measure7Actuals from "../../../data/entities/policy/miyagi_kpi_actuals_measure7_2024.json";
import measure8Evidence from "../../../data/entities/policy/miyagi_kpi_actuals_measure8_2024_evidence_packets.json";
import measure8Actuals from "../../../data/entities/policy/miyagi_kpi_actuals_measure8_2024.json";
import measure9Evidence from "../../../data/entities/policy/miyagi_kpi_actuals_measure9_2024_evidence_packets.json";
import measure9Actuals from "../../../data/entities/policy/miyagi_kpi_actuals_measure9_2024.json";

export type MiyagiAchievementRateStatus = "numeric" | "above_100" | "below_0";
export type MiyagiAchievementGrade = "A" | "B" | "C" | "D" | "not_set";

export type MiyagiAnnualResult = {
  reporting_period_original: "R3" | "R4" | "R5" | "R6";
  reporting_year: number;
  measurement_period_original: "R1" | "R2" | "R3" | "R4" | "R5" | "R6";
  measurement_year: number;
  value: number;
  value_text_original: string;
  unit_original: string;
  achievement_rate_text_original: string;
  achievement_rate_value: number | null;
  achievement_rate_status: MiyagiAchievementRateStatus;
  achievement_grade: MiyagiAchievementGrade;
};

export type MiyagiKpiActualLink = {
  id: string;
  target_group_id: string;
  series_id: string;
  linkage_status: "linked" | "needs_review";
  match_basis: "exact_name_and_unit" | "normalized_name_and_unit" | "definition_changed";
  source_indicator_number: number;
  source_indicator_name_original: string;
  source_pdf_page: number;
  achievement_rate_type_original: string;
  evaluation_baseline: {
    period_original: string;
    period_year: number;
    value: number;
    value_text_original: string;
    unit_original: string;
  };
  evaluation_target: {
    period_original: string;
    period_year: number;
    value: number;
    value_text_original: string;
    unit_original: string;
  };
  annual_results: MiyagiAnnualResult[];
  comparability_note_original: string;
  review_status: "reviewed";
  confidence: "high" | "medium";
};

export const reviewedMiyagiKpiActualLinks = [
  ...measure1Actuals.records,
  ...measure2Actuals.records,
  ...measure3Actuals.records,
  ...measure4Actuals.records,
  ...measure5Actuals.records,
  ...measure6Actuals.records,
  ...measure7Actuals.records,
  ...measure8Actuals.records,
  ...measure9Actuals.records,
] as MiyagiKpiActualLink[];
export const miyagiKpiActualEvidencePackets = [
  ...measure1Evidence,
  ...measure2Evidence,
  ...measure3Evidence,
  ...measure4Evidence,
  ...measure5Evidence,
  ...measure6Evidence,
  ...measure7Evidence,
  ...measure8Evidence,
  ...measure9Evidence,
];

export const miyagiKpiActualBySeriesId = new Map(
  reviewedMiyagiKpiActualLinks.map((record) => [record.series_id, record]),
);

export function latestMiyagiAnnualResult(record: MiyagiKpiActualLink) {
  return [...record.annual_results].sort(
    (left, right) => right.reporting_year - left.reporting_year,
  )[0];
}

export const miyagiKpiActualStats = {
  reviewedLinks: reviewedMiyagiKpiActualLinks.length,
  linkedSeries: reviewedMiyagiKpiActualLinks.filter(
    (record) => record.linkage_status === "linked",
  ).length,
  reviewNeededSeries: reviewedMiyagiKpiActualLinks.filter(
    (record) => record.linkage_status === "needs_review",
  ).length,
  annualResultRows: reviewedMiyagiKpiActualLinks.reduce(
    (total, record) => total + record.annual_results.length,
    0,
  ),
  evidencePackets: miyagiKpiActualEvidencePackets.length,
  subjectFiscalYear: measure9Actuals.subject_fiscal_year,
  evaluationFiscalYear: measure9Actuals.evaluation_fiscal_year,
};
