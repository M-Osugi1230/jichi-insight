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

function findDataRoot(): string {
  const candidates = [
    path.resolve(process.cwd(), "data"),
    path.resolve(process.cwd(), "../../data"),
  ];
  return candidates.find((candidate) => fs.existsSync(candidate)) ?? candidates[0];
}

export function loadPhase10Queue(): Phase10Queue {
  const queuePath = path.join(
    findDataRoot(),
    "catalog",
    "phase10_execution_queue.json",
  );
  return JSON.parse(fs.readFileSync(queuePath, "utf-8")) as Phase10Queue;
}

export function phase10DepthLabel(status: Phase10DepthStatus): string {
  return {
    not_indexed: "未索引",
    indexed: "入口確認",
    reviewed: "Reviewed",
    linked: "目標へ接続",
  }[status];
}
