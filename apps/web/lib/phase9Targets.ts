import fs from "node:fs";
import path from "node:path";

export type Phase9SummaryRecord = {
  prefecture_code: string;
  name: string;
  slug: string;
  batch_id: string;
  plan_title: string;
  plan_period: string;
  source_url: string;
  reviewed_target_statement_count: number;
  evidence_packet_count: number;
  document_count: number;
  extraction_error_count: number;
  route: string;
  review_status: "reviewed";
  policy_achievement_assessment_status: "not_assessed";
  ranking_eligibility: "excluded_until_comparability_verified";
};

export type Phase9Summary = {
  id: string;
  status: "reviewed_complete" | "generation_pending";
  prefecture_count: number;
  reviewed_target_statement_count: number;
  evidence_packet_count: number;
  evidence_coverage_percent: number;
  policy_achievement_assessed_count: number;
  ranking_eligible_record_count: number;
  records: Phase9SummaryRecord[];
  updated_at: string;
};

export type Phase9TargetRecord = {
  id: string;
  evidence_id: string;
  display_order: number;
  indicator_name_original: string;
  target_statement_original: string;
  numeric_tokens_original: string[];
  period_tokens_original: string[];
  matched_keywords: string[];
  keyword_match_kind: "explicit" | "table_header_context";
  unit_original: string | null;
  population_scope_original: string | null;
  aggregation_scope: string;
  target_operator: string;
  source_document_url: string;
  source_document_title: string;
  source_document_sha256: string;
  source_location: {
    location_kind: string;
    page?: number;
    sheet?: string;
    table?: number;
    row?: number;
  };
  plan_history_boundary: string;
  comparability: {
    status: "not_comparable";
    reasons: string[];
  };
  review_method: string;
  review_status: "reviewed";
  policy_achievement_assessment_status: "not_assessed";
};

export type Phase9Catalog = {
  id: string;
  prefecture_code: string;
  municipality_key: string;
  slug: string;
  name: string;
  batch_id: string;
  plan_title: string;
  plan_period: string;
  source_registry_path: string;
  source_id: string;
  source_title: string;
  source_url: string;
  documents: Array<{
    url: string;
    title: string;
    content_type: string;
    sha256: string;
    size_bytes: number;
    structural_count: number;
    extracted_row_count: number;
    reviewed_row_count: number;
  }>;
  reviewed_target_statement_count: number;
  evidence_packet_count: number;
  review_method: string;
  review_status: "reviewed";
  policy_achievement_assessment_status: "not_assessed";
  ranking_eligibility: "excluded_until_comparability_verified";
  records: Phase9TargetRecord[];
  updated_at: string;
};

const EMPTY_SUMMARY: Phase9Summary = {
  id: "phase9-reviewed-prefecture-summary",
  status: "generation_pending",
  prefecture_count: 0,
  reviewed_target_statement_count: 0,
  evidence_packet_count: 0,
  evidence_coverage_percent: 0,
  policy_achievement_assessed_count: 0,
  ranking_eligible_record_count: 0,
  records: [],
  updated_at: "2026-07-22",
};

function findDataRoot(): string {
  const candidates = [
    path.resolve(process.cwd(), "data"),
    path.resolve(process.cwd(), "../../data"),
  ];
  return candidates.find((candidate) => fs.existsSync(candidate)) ?? candidates[0];
}

const dataRoot = findDataRoot();

export function loadPhase9Summary(): Phase9Summary {
  const summaryPath = path.join(dataRoot, "catalog", "phase9_review_summary.json");
  if (!fs.existsSync(summaryPath)) {
    return EMPTY_SUMMARY;
  }
  return JSON.parse(fs.readFileSync(summaryPath, "utf-8")) as Phase9Summary;
}

export function loadPhase9Catalog(slug: string): Phase9Catalog | null {
  const summary = loadPhase9Summary();
  const record = summary.records.find((item) => item.slug === slug);
  if (!record) {
    return null;
  }
  const catalogPath = path.join(dataRoot, "reviewed", "phase9", `${record.prefecture_code}.json`);
  if (!fs.existsSync(catalogPath)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(catalogPath, "utf-8")) as Phase9Catalog;
}

export function phase9SourceLocation(record: Phase9TargetRecord): string {
  const location = record.source_location;
  const parts = [
    location.page ? `PDF ${location.page}頁` : null,
    location.sheet ? `シート「${location.sheet}」` : null,
    location.table ? `表${location.table}` : null,
    location.row ? `行${location.row}` : null,
  ].filter(Boolean);
  return parts.join(" / ") || location.location_kind;
}
