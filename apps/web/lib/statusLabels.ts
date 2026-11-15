import type { SourceRecord } from "./catalog";
import type { FiscalRecord } from "./finance";

/**
 * Shared presentation vocabulary for data status (Issue #5).
 *
 * Every status is rendered as a text label; color is only a supplement and
 * is never the sole carrier of meaning. Labels come from the canonical
 * record fields only — this module never invents a status for a record.
 */

export type StatusTone = "neutral" | "progress" | "verified" | "warning";

export type StatusPresentation = {
  label: string;
  tone: StatusTone;
};

const reviewStatusPresentations: Record<
  SourceRecord["review_status"],
  StatusPresentation
> = {
  verified: { label: "検証済み", tone: "verified" },
  reviewed: { label: "レビュー済み", tone: "verified" },
  extracted: { label: "抽出済み（未レビュー）", tone: "progress" },
  inferred: { label: "推定", tone: "warning" },
  missing: { label: "未確認", tone: "warning" },
};

export function sourceReviewStatusPresentation(
  reviewStatus: SourceRecord["review_status"],
): StatusPresentation {
  return reviewStatusPresentations[reviewStatus];
}

const confidenceLabels: Record<SourceRecord["confidence"], string> = {
  high: "信頼度：高",
  medium: "信頼度：中",
  low: "信頼度：低",
  not_assessable: "信頼度：評価不能",
};

export function sourceConfidenceLabel(
  confidence: SourceRecord["confidence"],
): string {
  return confidenceLabels[confidence];
}

const availabilityPresentations: Record<
  SourceRecord["availability"],
  StatusPresentation
> = {
  published: { label: "公開中", tone: "neutral" },
  not_published: { label: "未公表", tone: "warning" },
  not_found: { label: "資料未発見", tone: "warning" },
  restricted: { label: "公開制限あり", tone: "warning" },
  unknown: { label: "公開状況不明", tone: "warning" },
};

export function sourceAvailabilityPresentation(
  availability: SourceRecord["availability"],
): StatusPresentation {
  return availabilityPresentations[availability];
}

/**
 * Labels for the kind of statement being shown. A value taken directly from
 * a primary source is a fact; anything derived must say so, and an
 * evaluation must never be dressed up as a fact.
 */
export const statementKindLabels = {
  fact: "事実",
  normalizedComparison: "正規化した比較",
  interpretation: "解釈",
  evaluation: "評価",
} as const;

export type StatementKind = keyof typeof statementKindLabels;

const fiscalStageLabels: Record<FiscalRecord["stage"], string> = {
  initial_budget: "当初予算",
  revised_budget: "補正後予算",
  execution: "執行",
  settlement: "決算",
};

/**
 * The budget stage of a fiscal record, taken from the record itself.
 * (EvidencePanel previously printed 当初予算 for every record, including
 * settlement records.)
 */
export function fiscalStageLabel(stage: FiscalRecord["stage"]): string {
  return fiscalStageLabels[stage];
}
