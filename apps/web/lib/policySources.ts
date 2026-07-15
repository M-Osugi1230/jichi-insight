import policySourceCatalog from "../../../data/catalog/policy_sources.json";
import policyCollectionProfiles from "../../../data/entities/policy/policy_collection_profiles.json";

export type PolicySourceRole =
  | "strategic_plan"
  | "implementation_plan"
  | "annual_progress_report"
  | "annual_priority_program"
  | "project_review"
  | "progress_management";

export type PolicySourceRecord = {
  id: string;
  municipality_key: "fukuoka-prefecture" | "fukuoka-city" | "kitakyushu-city";
  organization: string;
  title: string;
  url: string;
  source_role: PolicySourceRole;
  format: "html" | "pdf";
  period_start: number | null;
  period_end: number | null;
  fiscal_year: number | null;
  published_at: string | null;
  collection_status: "indexed" | "ready_for_extraction" | "extracted" | "reviewed";
  extraction_targets: Array<
    "goals" | "measures" | "kpis" | "projects" | "budgets" | "results" | "issues" | "owners" | "timelines"
  >;
  review_status: "verified" | "reviewed" | "extracted" | "inferred" | "missing";
  confidence: "high" | "medium" | "low" | "not_assessable";
  notes: string;
};

export type PolicyCapabilityDimension =
  | "strategic_directions"
  | "implementation_plan"
  | "initiative_progress"
  | "numeric_targets"
  | "annual_reports"
  | "all_project_review"
  | "priority_project_sheets"
  | "budget_feedback"
  | "progress_management";

export type PolicyCollectionCapability = {
  dimension: PolicyCapabilityDimension;
  availability: "confirmed" | "partial" | "entry_point_only" | "unknown";
  count: number | null;
  period_start: number | null;
  period_end: number | null;
  statement: string;
  source_ids: string[];
  location_note: string;
};

export type PolicyCollectionProfile = {
  id: string;
  municipality_key: PolicySourceRecord["municipality_key"];
  capabilities: PolicyCollectionCapability[];
  extraction_readiness: "high" | "medium" | "low";
  next_priority: string;
  caveats: string[];
  reviewed_at: string;
  review_status: "reviewed" | "verified";
  confidence: "high" | "medium" | "low" | "not_assessable";
};

export const policySources = policySourceCatalog.records as PolicySourceRecord[];
export const policyProfiles = policyCollectionProfiles as PolicyCollectionProfile[];

export const policySourceRoleLabels: Record<PolicySourceRole, string> = {
  strategic_plan: "総合・基本計画",
  implementation_plan: "実施計画",
  annual_progress_report: "年度進捗報告",
  annual_priority_program: "年度主要施策",
  project_review: "事業点検",
  progress_management: "進行管理",
};

export const policyCapabilityLabels: Record<PolicyCapabilityDimension, string> = {
  strategic_directions: "計画の基本方向",
  implementation_plan: "実施計画",
  initiative_progress: "取組別の進捗",
  numeric_targets: "数値目標",
  annual_reports: "年度報告",
  all_project_review: "全事業点検",
  priority_project_sheets: "重点事業シート",
  budget_feedback: "予算編成への活用",
  progress_management: "進行管理",
};

export const extractionTargetLabels: Record<PolicySourceRecord["extraction_targets"][number], string> = {
  goals: "目標",
  measures: "施策",
  kpis: "KPI",
  projects: "事業",
  budgets: "予算",
  results: "実績",
  issues: "課題",
  owners: "担当",
  timelines: "期限",
};

export const policySourceMunicipalities = [
  { key: "fukuoka-prefecture" as const, name: "福岡県", type: "都道府県" },
  { key: "fukuoka-city" as const, name: "福岡市", type: "政令指定都市" },
  { key: "kitakyushu-city" as const, name: "北九州市", type: "政令指定都市" },
];

export function policySourcesForMunicipality(key: PolicySourceRecord["municipality_key"]) {
  return policySources.filter((source) => source.municipality_key === key);
}

export function policyProfileForMunicipality(key: PolicySourceRecord["municipality_key"]) {
  const profile = policyProfiles.find((item) => item.municipality_key === key);
  if (!profile) {
    throw new Error(`Missing policy collection profile: ${key}`);
  }
  return profile;
}

export const policySourceStats = {
  total: policySources.length,
  municipalities: new Set(policySources.map((source) => source.municipality_key)).size,
  readyForExtraction: policySources.filter(
    (source) => source.collection_status === "ready_for_extraction",
  ).length,
  pdfs: policySources.filter((source) => source.format === "pdf").length,
  roles: new Set(policySources.map((source) => source.source_role)).size,
};

export function policySourcePeriod(source: PolicySourceRecord) {
  if (source.fiscal_year) {
    return `${source.fiscal_year}年度`;
  }
  if (source.period_start && source.period_end) {
    return `${source.period_start}–${source.period_end}年度`;
  }
  return "期間を確認中";
}

export function policyCapabilityPeriod(capability: PolicyCollectionCapability) {
  if (capability.period_start && capability.period_end) {
    return `${capability.period_start}–${capability.period_end}年度`;
  }
  return null;
}
