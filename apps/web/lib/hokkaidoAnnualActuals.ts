import linkageIndex from "../../../data/catalog/hokkaido_annual_actual_linkage.json";
import linkagePart01 from "../../../data/catalog/hokkaido_annual_actual_linkage_part_01.json";
import linkagePart02 from "../../../data/catalog/hokkaido_annual_actual_linkage_part_02.json";

export type HokkaidoActualStatus = "linked" | "partial";

export type HokkaidoActualComponent = {
  label: string | null;
  unit: string | null;
  value_text: string;
  value: number | null;
  value_status: "numeric" | "textual";
};

export type HokkaidoActualRecord = {
  id: string;
  indicator_id: string;
  indicator_number: number;
  indicator_name: string;
  policy_direction_id: string;
  policy_field_ids: string[];
  linkage_status: HokkaidoActualStatus;
  partial_reason:
    | "target_version_changed"
    | "indicator_definition_or_numbering_changed"
    | "component_structure_changed"
    | null;
  source_indicator_name_text: string;
  actual_status: "available" | "available_raw_only" | "not_available" | "not_promoted";
  actual_value_text: string;
  actual_period_text: string;
  actual_components: HokkaidoActualComponent[];
  definition_text: string;
  source_number: number;
  pdf_page: number;
  related_source_locations: Array<{
    source_number: number;
    pdf_page: number;
    is_reprint: boolean;
  }>;
  boundary: string;
};

type LinkagePart = { records: HokkaidoActualRecord[] };

export const hokkaidoAnnualActualLinkage = linkageIndex;
export const hokkaidoAnnualActualRecords: HokkaidoActualRecord[] = [
  ...(linkagePart01 as LinkagePart).records,
  ...(linkagePart02 as LinkagePart).records,
];

export function hokkaidoStatusLabel(status: HokkaidoActualStatus): string {
  return status === "linked" ? "年度実績へ接続" : "版・定義の確認が必要";
}

export function partialReasonLabel(
  reason: HokkaidoActualRecord["partial_reason"],
): string {
  if (reason === "target_version_changed") return "目標版が変更";
  if (reason === "component_structure_changed") return "構成系列が変更";
  if (reason === "indicator_definition_or_numbering_changed") {
    return "指標定義・番号体系が変更";
  }
  return "—";
}

export function actualDisplay(record: HokkaidoActualRecord): string {
  if (record.linkage_status === "partial") return "接続保留";
  if (record.actual_status === "not_available") return "実績なし／未公表";
  return record.actual_value_text || "—";
}
