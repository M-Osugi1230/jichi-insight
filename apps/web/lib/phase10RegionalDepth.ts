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

export type RegionalDepthBatch = {
  slug: string;
  label: string;
  region: string;
  filename: string;
  route: string;
  prefecture_codes: string[];
};

export type RegionalDepthIndex = {
  id: "phase10-regional-depth-index";
  phase: 10;
  status: "in_progress" | "complete";
  batches: RegionalDepthBatch[];
  reviewed_prefecture_count: number;
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

export function loadPhase10RegionalDepth(
  filename: string,
): RegionalDepthReviews {
  return loadCatalog<RegionalDepthReviews>(filename);
}

export function loadPhase10RegionalDepthIndex(): RegionalDepthIndex {
  return loadCatalog<RegionalDepthIndex>("phase10_regional_depth_index.json");
}

export function loadPhase10RegionalDepthBySlug(
  slug: string,
): RegionalDepthReviews {
  const batch = loadPhase10RegionalDepthIndex().batches.find(
    (candidate) => candidate.slug === slug,
  );
  if (!batch) {
    throw new Error(`Unknown Phase 10 regional depth batch: ${slug}`);
  }
  return loadPhase10RegionalDepth(batch.filename);
}

export function loadAllPhase10RegionalDepth(): RegionalDepthReviews[] {
  return loadPhase10RegionalDepthIndex().batches.map((batch) =>
    loadPhase10RegionalDepth(batch.filename),
  );
}

export function loadPhase10TohokuDepth(): RegionalDepthReviews {
  return loadPhase10RegionalDepthBySlug("tohoku");
}

export function loadPhase10KantoDepth(): RegionalDepthReviews {
  return loadPhase10RegionalDepthBySlug("kanto");
}

export function loadPhase10ChubuDepth(): RegionalDepthReviews {
  return loadPhase10RegionalDepthBySlug("chubu");
}

export const regionalDepthLabels: Record<RegionalDepthDimension, string> = {
  annual_actuals: "年度実績",
  budget: "予算",
  settlement: "決算",
  priority_projects: "重点事業",
  audit: "監査",
};
