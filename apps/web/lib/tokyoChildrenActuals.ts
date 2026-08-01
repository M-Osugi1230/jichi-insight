import linkage from "../../../data/catalog/tokyo_children_annual_actual_linkage.json";

export type TokyoChildrenLinkageStatus = "linked" | "partial";

export type TokyoChildrenSeriesActual = {
  series_id: string;
  series_label: string | null;
  unit: string;
  catalog_role: "current" | "actual" | "baseline";
  actual_value: number | null;
  actual_value_text: string;
  actual_period: string;
  value_status: "numeric" | "textual" | "not_set";
};

export type TokyoChildrenActualRecord = {
  id: string;
  target_id: string;
  target_group_number: number;
  target_name: string;
  linkage_status: TokyoChildrenLinkageStatus;
  partial_reason:
    | "reporting_period_conflict"
    | "actual_value_and_period_conflict"
    | null;
  linked_series: TokyoChildrenSeriesActual[];
  conflict: Record<string, string> | null;
  source_pdf_page: number;
  source_alias: string;
  evaluation_status: "not_assessed";
  boundary: string;
};

export const tokyoChildrenAnnualActualLinkage = linkage;
export const tokyoChildrenAnnualActualRecords =
  linkage.records as TokyoChildrenActualRecord[];

export function tokyoChildrenStatusLabel(
  status: TokyoChildrenLinkageStatus,
): string {
  return status === "linked" ? "年度実績へ接続" : "文書間の差異を確認";
}

export function tokyoConflictLabel(
  reason: TokyoChildrenActualRecord["partial_reason"],
): string {
  if (reason === "reporting_period_conflict") {
    return "実績期間が不一致";
  }
  if (reason === "actual_value_and_period_conflict") {
    return "実績値と期間が不一致";
  }
  return "—";
}

export function seriesActualDisplay(
  series: TokyoChildrenSeriesActual,
): string {
  const label = series.series_label ? `${series.series_label}: ` : "";
  return `${label}${series.actual_value_text}${series.unit}（${series.actual_period}）`;
}
