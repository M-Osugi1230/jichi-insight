import linkageIndex from "../../../data/catalog/miyagi_project_money_linkage.json";
import linkagePart01 from "../../../data/catalog/miyagi_project_money_linkage_part_01.json";
import linkagePart02 from "../../../data/catalog/miyagi_project_money_linkage_part_02.json";
import linkagePart03 from "../../../data/catalog/miyagi_project_money_linkage_part_03.json";
import linkagePart04 from "../../../data/catalog/miyagi_project_money_linkage_part_04.json";

export type MiyagiMoneyStatus = "linked" | "partial" | "not_linked";

export type MiyagiMoneyCandidate = {
  measure_id: string | null;
  policy_id: string | null;
  project_name: string;
  department: string;
  office: string;
  settlement_amount_thousand_yen: number;
  settlement_pdf_page: number;
};

export type MiyagiProjectMoneyRecord = {
  id: string;
  linkage_status: MiyagiMoneyStatus;
  match_basis: string;
  policy_id: string;
  measure_id: string;
  project_name: string;
  project_name_normalized: string;
  department: string;
  office: string;
  implementation_period: string;
  budget_period: "令和8年度";
  budget_amount_thousand_yen: number;
  budget_amount_text: string;
  budget_pdf_page: number;
  settlement_period: "令和6年度" | null;
  settlement_amount_thousand_yen: number | null;
  settlement_amount_text: string | null;
  settlement_pdf_page: number | null;
  settlement_project_number_text: string | null;
  settlement_candidates: MiyagiMoneyCandidate[];
  boundary: string;
};

type LinkagePart = { records: MiyagiProjectMoneyRecord[] };

export const miyagiProjectMoneyLinkage = linkageIndex;
export const miyagiProjectMoneyRecords: MiyagiProjectMoneyRecord[] = [
  ...(linkagePart01 as LinkagePart).records,
  ...(linkagePart02 as LinkagePart).records,
  ...(linkagePart03 as LinkagePart).records,
  ...(linkagePart04 as LinkagePart).records,
];

export function miyagiMoneyStatusLabel(status: MiyagiMoneyStatus): string {
  return {
    linked: "同一事業系列へ接続",
    partial: "追加確認が必要",
    not_linked: "前年度同一事業なし",
  }[status];
}

export function formatThousandYen(value: number | null): string {
  return value === null ? "—" : `${value.toLocaleString("ja-JP")}千円`;
}
