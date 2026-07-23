import fs from "node:fs";
import path from "node:path";

export type Phase10DepthStatus = "not_indexed" | "indexed" | "reviewed" | "linked";

export type Phase10Wave1Record = {
  prefecture_code: string;
  name: string;
  region: string;
  status: "queued" | "review_ready" | "linked_baseline" | "complete";
  current_depth: {
    target_statements: "reviewed";
    annual_evaluation: Phase10DepthStatus;
    budget: Phase10DepthStatus;
    project_evaluation: Phase10DepthStatus;
    contracts: Phase10DepthStatus;
  };
  next_gate:
    | "source_inventory"
    | "annual_actuals_linkage"
    | "budget_linkage"
    | "project_spine"
    | "publication_verification";
  next_action: string;
};

export type Phase10Queue = {
  id: string;
  phase: 10;
  status: "in_progress" | "verification_pending" | "complete";
  scope_version: string;
  current_focus: "annual_actuals_money_action_spine";
  active_prefecture_code: string;
  prefecture_order: string[];
  waves: Array<{
    id: string;
    prefecture_codes: string[];
    objective: string;
  }>;
  default_depth: Phase10Wave1Record["current_depth"];
  wave1_records: Phase10Wave1Record[];
  counts: {
    total_prefectures: number;
    wave1_prefectures: number;
    target_statements_reviewed: number;
    annual_evaluation_linked: number;
    annual_evaluation_indexed: number;
    budget_reviewed: number;
    project_evaluation_indexed_or_better: number;
    contracts_indexed_or_better: number;
  };
  policy_achievement_assessment_status: "not_assessed";
  ranking_eligibility: "excluded_until_comparability_verified";
  updated_at: string;
};

export type Phase10SourceRecord = {
  id: string;
  prefecture_code: string;
  name: string;
  category: "annual_evaluation" | "budget" | "project_evaluation" | "contracts";
  coverage_role: string;
  title: string;
  url: string;
  official_owner: string;
  source_status: "indexed" | "reviewed";
  linkage_status: "not_linked" | "candidate_linkage" | "linked_existing";
  currentness_status: "current" | "latest_available";
  reporting_period: string | null;
  plan_alignment: "current_plan" | "current_budget_cycle" | "crosswalk_required";
  supports: string[];
  scope_boundary: string;
  observed_at: string;
};

export type Phase10SourceInventory = {
  id: string;
  status: "in_progress" | "verification_pending" | "complete";
  prefecture_codes: string[];
  categories: Phase10SourceRecord["category"][];
  records: Phase10SourceRecord[];
  summary: {
    prefecture_count: number;
    source_count: number;
    category_prefecture_counts: Record<Phase10SourceRecord["category"], number>;
    linked_existing_source_count: number;
    candidate_linkage_source_count: number;
    not_linked_source_count: number;
  };
  policy_achievement_assessment_status: "not_assessed";
  updated_at: string;
};

function findDataRoot(): string {
  const candidates = [
    path.resolve(process.cwd(), "data"),
    path.resolve(process.cwd(), "../../data"),
  ];
  return candidates.find((candidate) => fs.existsSync(candidate)) ?? candidates[0];
}

function loadCatalog<T>(filename: string): T {
  const catalogPath = path.join(findDataRoot(), "catalog", filename);
  return JSON.parse(fs.readFileSync(catalogPath, "utf-8")) as T;
}

export function loadPhase10Queue(): Phase10Queue {
  return loadCatalog<Phase10Queue>("phase10_execution_queue.json");
}

export function loadPhase10SourceInventory(): Phase10SourceInventory {
  return loadCatalog<Phase10SourceInventory>("phase10_wave1_source_inventory.json");
}

export function phase10SourcesByPrefecture(
  inventory: Phase10SourceInventory,
): Map<string, Phase10SourceRecord[]> {
  const result = new Map<string, Phase10SourceRecord[]>();
  for (const record of inventory.records) {
    result.set(record.prefecture_code, [
      ...(result.get(record.prefecture_code) ?? []),
      record,
    ]);
  }
  return result;
}

export function phase10DepthLabel(status: Phase10DepthStatus): string {
  return {
    not_indexed: "未索引",
    indexed: "入口確認",
    reviewed: "Reviewed",
    linked: "目標へ接続",
  }[status];
}
