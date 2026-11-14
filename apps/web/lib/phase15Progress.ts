import phase15QueueJson from "../../../data/catalog/phase15_core_capital_review_queue.json";

/**
 * Public, read-only Phase 15 state.
 *
 * The canonical review queue is the sole source of truth. Staged candidates are
 * deliberately not loaded here: a candidate awaiting human review is not a
 * published Reviewed record.
 */
export type Phase15ReviewStatus =
  | "reviewed_complete"
  | "review_in_progress"
  | "pending_record_review"
  | "blocked_source_inventory";

type Phase15QueueItem = {
  sequence: number;
  wave: number;
  official_code: string;
  name_ja: string;
  prefecture_name_ja: string;
  phase14_role: string;
  status: Phase15ReviewStatus;
  source_inventory_path: string;
  completion_path: string | null;
};

type Phase15Queue = {
  updated_at: string;
  summary: {
    target_count: number;
    reviewed_complete_count: number;
    review_in_progress_count: number;
    pending_record_review_count: number;
    blocked_source_inventory_count: number;
    next_official_code: string | null;
  };
  execution_queue: Phase15QueueItem[];
};

const queue = phase15QueueJson as unknown as Phase15Queue;

export const phase15StatusLabels: Record<Phase15ReviewStatus, string> = {
  reviewed_complete: "一次資料のレビュー完了",
  review_in_progress: "レビュー進行中",
  pending_record_review: "個票レビュー待ち",
  blocked_source_inventory: "資料確認に課題あり",
};

const counted = {
  reviewed: queue.execution_queue.filter((item) => item.status === "reviewed_complete").length,
  inProgress: queue.execution_queue.filter((item) => item.status === "review_in_progress").length,
  pending: queue.execution_queue.filter((item) => item.status === "pending_record_review").length,
  blocked: queue.execution_queue.filter((item) => item.status === "blocked_source_inventory").length,
};

// A publication build must fail rather than display inconsistent review counts.
if (
  queue.execution_queue.length !== queue.summary.target_count ||
  counted.reviewed !== queue.summary.reviewed_complete_count ||
  counted.inProgress !== queue.summary.review_in_progress_count ||
  counted.pending !== queue.summary.pending_record_review_count ||
  counted.blocked !== queue.summary.blocked_source_inventory_count ||
  Object.values(counted).reduce((sum, count) => sum + count, 0) !== queue.execution_queue.length ||
  queue.execution_queue.some((item) => item.status === "reviewed_complete" && !item.completion_path)
) {
  throw new Error("Phase 15 publication state does not match the canonical review queue.");
}

export const phase15Progress = {
  updatedAt: queue.updated_at,
  total: queue.summary.target_count,
  reviewed: counted.reviewed,
  inProgress: counted.inProgress,
  pending: counted.pending,
  blocked: counted.blocked,
  nextMunicipality:
    queue.execution_queue.find((item) => item.official_code === queue.summary.next_official_code)?.name_ja ??
    null,
  municipalities: queue.execution_queue.map((item) => ({
    sequence: item.sequence,
    wave: item.wave,
    officialCode: item.official_code,
    name: item.name_ja,
    prefecture: item.prefecture_name_ja,
    role: item.phase14_role,
    status: item.status,
    sourceInventoryPath: item.source_inventory_path,
    completionPath: item.completion_path,
  })),
};
