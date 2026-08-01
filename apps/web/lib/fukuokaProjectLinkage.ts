import linkageIndex from "../../../data/catalog/fukuoka_project_linkage.json";
import linkagePart01 from "../../../data/catalog/fukuoka_project_linkage_part_01.json";
import linkagePart02 from "../../../data/catalog/fukuoka_project_linkage_part_02.json";
import linkagePart03 from "../../../data/catalog/fukuoka_project_linkage_part_03.json";

export type FukuokaProjectStatus = "linked" | "partial" | "not_linked";

export type FukuokaPageMatch = {
  pdf_page: number;
  matched_alias: string;
};

export type FukuokaTargetMatch = {
  target_id: string;
  initiative_id: string;
  indicator_name: string;
  match_basis: string;
};

export type FukuokaProjectLinkageRecord = {
  id: string;
  linkage_status: FukuokaProjectStatus;
  match_basis: string;
  evaluation_number: number;
  project_name: string;
  project_name_normalized: string;
  project_aliases: string[];
  department_office: string;
  fy2025_project_cost_thousand_yen: number;
  purpose: string;
  content: string;
  indicator_text: string;
  direction: string;
  evaluation_summary_pdf_page: number;
  target_matches: FukuokaTargetMatch[];
  budget_matches: FukuokaPageMatch[];
  settlement_matches: FukuokaPageMatch[];
  boundary: string;
};

type LinkagePart = { records: FukuokaProjectLinkageRecord[] };

export const fukuokaProjectLinkage = linkageIndex;
export const fukuokaProjectLinkageRecords: FukuokaProjectLinkageRecord[] = [
  ...(linkagePart01 as LinkagePart).records,
  ...(linkagePart02 as LinkagePart).records,
  ...(linkagePart03 as LinkagePart).records,
];

export function projectStatusLabel(status: FukuokaProjectStatus): string {
  return {
    linked: "完全名称一致候補",
    partial: "追加確認が必要",
    not_linked: "金額資料への接続なし",
  }[status];
}

export function formatProjectCost(value: number): string {
  return `${value.toLocaleString("ja-JP")}千円`;
}
