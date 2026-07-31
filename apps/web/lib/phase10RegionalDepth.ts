import fs from "node:fs";
import path from "node:path";

export type RegionalDepthDimension =
  | "annual_actuals"
  | "budget"
  | "settlement"
  | "priority_projects"
  | "audit";

export type RegionalDepthSource = {
  title: string;
  url: string;
  official_owner: string;
  reporting_period: string;
  claim: string;
  boundary: string;
};

export type RegionalDepthRecord = {
  prefecture_code: string;
  name: string;
  region: string;
  sources: Record<RegionalDepthDimension, RegionalDepthSource>;
  next_linkage: string;
};

export type RegionalDepthReviews = {
  id: string;
  phase: 10;
  status: "reviewed";
  batch_id: string;
  region: string;
  prefecture_codes: string[];
  dimensions: RegionalDepthDimension[];
  records: RegionalDepthRecord[];
  summary: {
    prefecture_count: number;
    dimension_count: number;
    reviewed_source_count: number;
    dimension_reviewed_counts: Record<RegionalDepthDimension, number>;
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

export function loadPhase10RegionalDepth(
  filename: string,
): RegionalDepthReviews {
  const catalogPath = path.join(findDataRoot(), "catalog", filename);
  return JSON.parse(
    fs.readFileSync(catalogPath, "utf-8"),
  ) as RegionalDepthReviews;
}

export function loadPhase10TohokuDepth(): RegionalDepthReviews {
  return loadPhase10RegionalDepth("phase10_tohoku_depth_reviews.json");
}

export function loadPhase10KantoDepth(): RegionalDepthReviews {
  return loadPhase10RegionalDepth("phase10_kanto_depth_reviews.json");
}

export const regionalDepthLabels: Record<RegionalDepthDimension, string> = {
  annual_actuals: "年度実績",
  budget: "予算",
  settlement: "決算",
  priority_projects: "重点事業",
  audit: "監査",
};
