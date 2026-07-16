import policySourceCatalog from "../../../data/catalog/policy_sources.json";
import reviewQueue from "../../../data/catalog/wave1_policy_review_queue.json";

import { nationwidePrefectureCoverage } from "./nationwideCoverage";

export type PolicyReviewQueueStatus =
  | "reviewed_reference"
  | "active_review"
  | "queued";

export type SourceInventoryStatus =
  | "reviewed"
  | "policy_hierarchy_reviewed"
  | "plan_kpi_entry_indexed"
  | "plan_followup_entry_indexed"
  | "strategic_plan_indexed";

export type PolicyReviewNextGate =
  | "source_inventory"
  | "policy_hierarchy"
  | "kpi_catalog"
  | "actuals_linkage";

type QueueRecord = {
  prefecture_code: string;
  municipality_key: string;
  order: number;
  status: PolicyReviewQueueStatus;
  source_ids: string[];
  current_plan_title: string;
  source_inventory_status: SourceInventoryStatus;
  next_gate: PolicyReviewNextGate;
  next_action: string;
  priority_basis: string;
};

type PolicySourceRecord = {
  id: string;
  title: string;
  url: string;
  collection_status: "indexed" | "ready_for_extraction" | "extracted" | "reviewed";
  review_status: "verified" | "reviewed" | "extracted" | "inferred" | "missing";
};

const sourcesById = new Map(
  (policySourceCatalog.records as PolicySourceRecord[]).map((source) => [
    source.id,
    source,
  ]),
);
const prefecturesByCode = new Map(
  nationwidePrefectureCoverage.map((prefecture) => [
    prefecture.prefecture_code,
    prefecture,
  ]),
);

export const waveOnePolicyReviewQueue = (reviewQueue.items as QueueRecord[]).map(
  (item) => {
    const prefecture = prefecturesByCode.get(item.prefecture_code);
    if (!prefecture) {
      throw new Error(`Unknown Wave 1 prefecture code: ${item.prefecture_code}`);
    }

    const sources = item.source_ids.map((sourceId) => {
      const source = sourcesById.get(sourceId);
      if (!source) {
        throw new Error(`Unknown policy source: ${sourceId}`);
      }
      return source;
    });

    return {
      ...item,
      name: prefecture.name,
      sources,
    };
  },
);

export const waveOnePolicyReviewStats = {
  total: waveOnePolicyReviewQueue.length,
  reviewedReferences: waveOnePolicyReviewQueue.filter(
    (item) => item.status === "reviewed_reference",
  ).length,
  activeReviews: waveOnePolicyReviewQueue.filter(
    (item) => item.status === "active_review",
  ).length,
  queued: waveOnePolicyReviewQueue.filter((item) => item.status === "queued")
    .length,
  activePrefectureCode: reviewQueue.active_prefecture_code,
  completedPrefectureCodes: reviewQueue.completed_prefecture_codes,
  updatedAt: reviewQueue.updated_at,
};

export function policyReviewStatusLabel(status: PolicyReviewQueueStatus) {
  const labels: Record<PolicyReviewQueueStatus, string> = {
    reviewed_reference: "Reviewed基準実装",
    active_review: "Reviewed化作業中",
    queued: "作業待ち",
  };
  return labels[status];
}

export function policyReviewStatusTone(status: PolicyReviewQueueStatus) {
  if (status === "reviewed_reference") return "verified" as const;
  if (status === "active_review") return "progress" as const;
  return "neutral" as const;
}

export function sourceInventoryStatusLabel(status: SourceInventoryStatus) {
  const labels: Record<SourceInventoryStatus, string> = {
    reviewed: "政策・KPI資料Reviewed",
    policy_hierarchy_reviewed: "政策体系Reviewed・KPI索引中",
    plan_kpi_entry_indexed: "計画・指標入口確認済み",
    plan_followup_entry_indexed: "計画・進捗入口確認済み",
    strategic_plan_indexed: "現行計画入口確認済み",
  };
  return labels[status];
}

export function policyReviewNextGateLabel(gate: PolicyReviewNextGate) {
  const labels: Record<PolicyReviewNextGate, string> = {
    source_inventory: "関連資料の固定",
    policy_hierarchy: "政策体系の照合",
    kpi_catalog: "KPIカタログ化",
    actuals_linkage: "年度実績との接続",
  };
  return labels[gate];
}
