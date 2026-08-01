import fs from "node:fs";
import path from "node:path";

export type Phase10DepthStatus =
  | "not_indexed"
  | "indexed"
  | "reviewed"
  | "linked";

export type Phase10DimensionId =
  | "target_statements"
  | "evidence_packets"
  | "annual_actuals"
  | "budget"
  | "settlement"
  | "priority_projects"
  | "contracts"
  | "assembly"
  | "audit"
  | "executive_manifesto"
  | "publication";

export type Phase10UniformDepth = Record<
  Phase10DimensionId,
  Phase10DepthStatus
>;

export type Phase10UniformRecord = {
  prefecture_code: string;
  name: string;
  region: string;
  status:
    | "queued"
    | "source_indexing"
    | "linkage_in_progress"
    | "review_ready"
    | "complete";
  current_depth: Phase10UniformDepth;
  gap_count: number;
  next_gate:
    | "source_inventory"
    | "annual_actuals_linkage"
    | "money_linkage"
    | "action_linkage"
    | "accountability_linkage"
    | "publication_verification";
  next_action: string;
};

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

export type Phase10Uniformity = {
  id: "phase10-nationwide-uniform-depth";
  phase: 10;
  status: "in_progress" | "verification_pending" | "complete";
  scope_version: string;
  dimensions: Array<{
    id: Phase10DimensionId;
    label: string;
    completion_status: Phase10DepthStatus;
  }>;
  default_depth: Phase10UniformDepth;
  default_work: {
    status: Phase10UniformRecord["status"];
    next_gate: Phase10UniformRecord["next_gate"];
    next_action_template: string;
  };
  overrides: Record<
    string,
    {
      status: Phase10UniformRecord["status"];
      current_depth: Partial<Phase10UniformDepth>;
      next_gate: Phase10UniformRecord["next_gate"];
      next_action: string;
    }
  >;
  completion_rule: {
    description: string;
    required_prefecture_count: 47;
    allow_partial_complete: false;
  };
  policy_achievement_assessment_status: "not_assessed";
  ranking_eligibility: "excluded_until_comparability_verified";
  updated_at: string;
};

export type Phase10SourceRecord = {
  id: string;
  prefecture_code: string;
  name: string;
  category:
    | "annual_evaluation"
    | "budget"
    | "project_evaluation"
    | "contracts";
  coverage_role: string;
  title: string;
  url: string;
  official_owner: string;
  source_status: "indexed" | "reviewed";
  linkage_status: "not_linked" | "candidate_linkage" | "linked_existing";
  currentness_status: "current" | "latest_available";
  reporting_period: string | null;
  plan_alignment:
    | "current_plan"
    | "current_budget_cycle"
    | "crosswalk_required";
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
    category_prefecture_counts: Record<
      Phase10SourceRecord["category"],
      number
    >;
    linked_existing_source_count: number;
    candidate_linkage_source_count: number;
    not_linked_source_count: number;
  };
  policy_achievement_assessment_status: "not_assessed";
  updated_at: string;
};

export type Phase10ReferenceReview = {
  id: string;
  prefecture_code: "04" | "40";
  name: "宮城県" | "福岡県";
  dimension:
    | "annual_actuals"
    | "budget"
    | "settlement"
    | "priority_projects"
    | "assembly"
    | "audit";
  resulting_depth: "indexed" | "reviewed" | "linked";
  title: string;
  url: string;
  official_owner: string;
  reporting_period: string;
  relationship: string;
  claims: string[];
  boundary: string;
  observed_at: string;
};

export type Phase10ReferenceReviews = {
  id: "phase10-reference-depth-reviews";
  status: "reviewed";
  prefecture_codes: Array<"04" | "40">;
  records: Phase10ReferenceReview[];
  summary: {
    prefecture_count: number;
    record_count: number;
    dimension_prefecture_counts: Record<
      Phase10ReferenceReview["dimension"],
      number
    >;
    resulting_depth_counts: Record<
      Phase10ReferenceReview["resulting_depth"],
      number
    >;
  };
  policy_achievement_assessment_status: "not_assessed";
  updated_at: string;
};

export type Phase10AnchorDimension =
  | "annual_actuals"
  | "budget"
  | "settlement"
  | "priority_projects"
  | "audit";

export type Phase10AnchorSource = {
  title: string;
  url: string;
  official_owner: string;
  reporting_period: string;
  claim: string;
  boundary: string;
};

export type Phase10AnchorRecord = {
  prefecture_code: "01" | "13" | "23" | "27" | "34" | "37" | "47";
  name:
    | "北海道"
    | "東京都"
    | "愛知県"
    | "大阪府"
    | "広島県"
    | "香川県"
    | "沖縄県";
  region: string;
  sources: Record<Phase10AnchorDimension, Phase10AnchorSource>;
  next_linkage: string;
};

export type Phase10AnchorReviews = {
  id: "phase10-anchor-depth-reviews";
  status: "reviewed";
  prefecture_codes: Phase10AnchorRecord["prefecture_code"][];
  dimensions: Phase10AnchorDimension[];
  records: Phase10AnchorRecord[];
  summary: {
    prefecture_count: 7;
    dimension_count: 5;
    reviewed_source_count: 35;
    dimension_reviewed_counts: Record<Phase10AnchorDimension, 7>;
  };
  policy_achievement_assessment_status: "not_assessed";
  updated_at: string;
};

type RegionalDepthIndex = {
  batches: Array<{ filename: string }>;
};

type RegionalDepthReviews = {
  records: Array<{
    prefecture_code: string;
    next_linkage: string;
  }>;
};

const prefectures = [
  ["01", "北海道", "北海道"],
  ["02", "青森県", "東北"],
  ["03", "岩手県", "東北"],
  ["04", "宮城県", "東北"],
  ["05", "秋田県", "東北"],
  ["06", "山形県", "東北"],
  ["07", "福島県", "東北"],
  ["08", "茨城県", "関東"],
  ["09", "栃木県", "関東"],
  ["10", "群馬県", "関東"],
  ["11", "埼玉県", "関東"],
  ["12", "千葉県", "関東"],
  ["13", "東京都", "関東"],
  ["14", "神奈川県", "関東"],
  ["15", "新潟県", "中部"],
  ["16", "富山県", "中部"],
  ["17", "石川県", "中部"],
  ["18", "福井県", "中部"],
  ["19", "山梨県", "中部"],
  ["20", "長野県", "中部"],
  ["21", "岐阜県", "中部"],
  ["22", "静岡県", "中部"],
  ["23", "愛知県", "中部"],
  ["24", "三重県", "近畿"],
  ["25", "滋賀県", "近畿"],
  ["26", "京都府", "近畿"],
  ["27", "大阪府", "近畿"],
  ["28", "兵庫県", "近畿"],
  ["29", "奈良県", "近畿"],
  ["30", "和歌山県", "近畿"],
  ["31", "鳥取県", "中国"],
  ["32", "島根県", "中国"],
  ["33", "岡山県", "中国"],
  ["34", "広島県", "中国"],
  ["35", "山口県", "中国"],
  ["36", "徳島県", "四国"],
  ["37", "香川県", "四国"],
  ["38", "愛媛県", "四国"],
  ["39", "高知県", "四国"],
  ["40", "福岡県", "九州・沖縄"],
  ["41", "佐賀県", "九州・沖縄"],
  ["42", "長崎県", "九州・沖縄"],
  ["43", "熊本県", "九州・沖縄"],
  ["44", "大分県", "九州・沖縄"],
  ["45", "宮崎県", "九州・沖縄"],
  ["46", "鹿児島県", "九州・沖縄"],
  ["47", "沖縄県", "九州・沖縄"],
] as const;

const statusRank: Record<Phase10DepthStatus, number> = {
  not_indexed: 0,
  indexed: 1,
  reviewed: 2,
  linked: 3,
};

function findDataRoot(): string {
  const candidates = [
    path.resolve(process.cwd(), "data"),
    path.resolve(process.cwd(), "../../data"),
  ];
  return candidates.find((candidate) => fs.existsSync(candidate)) ?? candidates[0];
}

function loadCatalog<T>(filename: string): T {
  return JSON.parse(
    fs.readFileSync(path.join(findDataRoot(), "catalog", filename), "utf-8"),
  ) as T;
}

export function loadPhase10Queue(): Phase10Queue {
  return loadCatalog<Phase10Queue>("phase10_execution_queue.json");
}

export function loadPhase10Uniformity(): Phase10Uniformity {
  const uniformity = loadCatalog<Phase10Uniformity>("phase10_uniformity.json");
  const index = loadCatalog<RegionalDepthIndex>(
    "phase10_regional_depth_index.json",
  );

  for (const batch of index.batches) {
    const reviews = loadCatalog<RegionalDepthReviews>(batch.filename);
    for (const record of reviews.records) {
      const existing = uniformity.overrides[record.prefecture_code];
      uniformity.overrides[record.prefecture_code] = {
        status: existing?.status ?? "linkage_in_progress",
        current_depth: {
          ...(existing?.current_depth ?? {}),
          annual_actuals: "reviewed",
          budget: "reviewed",
          settlement: "reviewed",
          priority_projects: "reviewed",
          audit: "reviewed",
        },
        next_gate: existing?.next_gate ?? "annual_actuals_linkage",
        next_action: existing?.next_action ?? record.next_linkage,
      };
    }
  }

  return uniformity;
}

export function phase10UniformRecords(
  uniformity: Phase10Uniformity,
): Phase10UniformRecord[] {
  return prefectures.map(([prefecture_code, name, region]) => {
    const override = uniformity.overrides[prefecture_code];
    const current_depth = {
      ...uniformity.default_depth,
      ...(override?.current_depth ?? {}),
    };
    const gap_count = uniformity.dimensions.filter(
      (dimension) =>
        statusRank[current_depth[dimension.id]] <
        statusRank[dimension.completion_status],
    ).length;
    return {
      prefecture_code,
      name,
      region,
      status: override?.status ?? uniformity.default_work.status,
      current_depth,
      gap_count,
      next_gate: override?.next_gate ?? uniformity.default_work.next_gate,
      next_action:
        override?.next_action ??
        uniformity.default_work.next_action_template.replace("{name}", name),
    };
  });
}

export function phase10UniformSummary(
  uniformity: Phase10Uniformity,
  records: Phase10UniformRecord[],
) {
  const summary = Object.fromEntries(
    uniformity.dimensions.map((dimension) => [
      dimension.id,
      { not_indexed: 0, indexed: 0, reviewed: 0, linked: 0 },
    ]),
  ) as Record<Phase10DimensionId, Record<Phase10DepthStatus, number>>;
  for (const record of records) {
    for (const dimension of uniformity.dimensions) {
      summary[dimension.id][record.current_depth[dimension.id]] += 1;
    }
  }
  return {
    ...summary,
    prefecture_count: records.length,
    uniform_depth_complete: records.filter((record) => record.gap_count === 0)
      .length,
  };
}

export function loadPhase10SourceInventory(): Phase10SourceInventory {
  return loadCatalog<Phase10SourceInventory>(
    "phase10_wave1_source_inventory.json",
  );
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

export function loadPhase10ReferenceReviews(): Phase10ReferenceReviews {
  return loadCatalog<Phase10ReferenceReviews>(
    "phase10_reference_depth_reviews.json",
  );
}

export function phase10ReferenceReviewsByPrefecture(
  reviews: Phase10ReferenceReviews,
): Map<string, Phase10ReferenceReview[]> {
  const result = new Map<string, Phase10ReferenceReview[]>();
  for (const record of reviews.records) {
    result.set(record.prefecture_code, [
      ...(result.get(record.prefecture_code) ?? []),
      record,
    ]);
  }
  return result;
}

export function loadPhase10AnchorReviews(): Phase10AnchorReviews {
  return loadCatalog<Phase10AnchorReviews>(
    "phase10_anchor_depth_reviews.json",
  );
}

export function phase10DepthLabel(status: Phase10DepthStatus): string {
  return {
    not_indexed: "未索引",
    indexed: "入口確認",
    reviewed: "Reviewed",
    linked: "目標へ接続",
  }[status];
}

export function phase10UniformRecordStatusLabel(
  status: Phase10UniformRecord["status"],
): string {
  return {
    queued: "資料索引待ち",
    source_indexing: "資料索引中",
    linkage_in_progress: "接続作業中",
    review_ready: "公開検証待ち",
    complete: "同一粒度完了",
  }[status];
}
