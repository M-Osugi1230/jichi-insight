import linkageIndex from "../../../data/catalog/fukuoka_annual_actual_linkage.json";
import linkagePart01 from "../../../data/catalog/fukuoka_annual_actual_linkage_part_01.json";
import linkagePart02 from "../../../data/catalog/fukuoka_annual_actual_linkage_part_02.json";
import linkagePart03 from "../../../data/catalog/fukuoka_annual_actual_linkage_part_03.json";
import linkagePart04 from "../../../data/catalog/fukuoka_annual_actual_linkage_part_04.json";

export type FukuokaActualLinkageStatus =
  | "linked"
  | "partial"
  | "not_linked";

export type FukuokaActualMatchBasis =
  | "normalized_indicator_exact"
  | "reviewed_alias"
  | "not_present_in_fy2024_progress_report";

export type FukuokaActualTargetVersionStatus =
  | "same_target_definition"
  | "revised_target_detected"
  | "source_row_not_found";

export type FukuokaAnnualActualRecord = {
  target_id: string;
  linkage_status: FukuokaActualLinkageStatus;
  match_basis: FukuokaActualMatchBasis;
  source_pdf_page: number | null;
  source_initial_value_text: string | null;
  source_target_value_text: string | null;
  actual_value_text: string | null;
  actual_period_text: string | null;
  target_version_status: FukuokaActualTargetVersionStatus;
  source_indicator_name?: string;
  alias_review_note?: string;
};

export type FukuokaAnnualActualLinkageIndex = {
  id: "fukuoka-prefecture-fy2024-annual-actual-linkage";
  prefecture_code: "40";
  status: "reviewed";
  source: {
    title: string;
    url: string;
    official_owner: string;
    reporting_period: "令和6年度";
    pdf_page_count: 61;
    observed_at: string;
  };
  target_count: 118;
  part_files: string[];
  summary: {
    linked_target_count: 86;
    partial_target_count: 12;
    not_linked_target_count: 20;
    normalized_exact_match_count: 88;
    reviewed_alias_match_count: 10;
    revised_target_detected_count: 12;
    source_row_not_found_count: 20;
  };
  boundaries: Record<FukuokaActualLinkageStatus, string>;
  evaluation_status: "not_assessed";
  updated_at: string;
};

type FukuokaAnnualActualPart = {
  records: FukuokaAnnualActualRecord[];
};

export const fukuokaAnnualActualLinkage =
  linkageIndex as FukuokaAnnualActualLinkageIndex;

export const fukuokaAnnualActualRecords: FukuokaAnnualActualRecord[] = [
  ...(linkagePart01 as FukuokaAnnualActualPart).records,
  ...(linkagePart02 as FukuokaAnnualActualPart).records,
  ...(linkagePart03 as FukuokaAnnualActualPart).records,
  ...(linkagePart04 as FukuokaAnnualActualPart).records,
];

export const fukuokaAnnualActualByTargetId = new Map(
  fukuokaAnnualActualRecords.map((record) => [record.target_id, record]),
);

export function fukuokaAnnualActualForTarget(
  targetId: string,
): FukuokaAnnualActualRecord | null {
  return fukuokaAnnualActualByTargetId.get(targetId) ?? null;
}

export function fukuokaAnnualActualStatus(
  targetId: string,
): FukuokaActualLinkageStatus {
  return fukuokaAnnualActualForTarget(targetId)?.linkage_status ?? "not_linked";
}

export function fukuokaAnnualActualStatusLabel(
  status: FukuokaActualLinkageStatus,
): string {
  return {
    linked: "年度実績へ接続",
    partial: "目標版の再確認",
    not_linked: "別資料を探索",
  }[status];
}
