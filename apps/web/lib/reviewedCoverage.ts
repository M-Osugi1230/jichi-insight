import phase10CompletionJson from "../../../data/catalog/phase10_completion.json";
import phase10QueueJson from "../../../data/catalog/phase10_execution_queue.json";
import phase9SummaryJson from "../../../data/catalog/phase9_review_summary.json";
import miyagiReviewManifestJson from "../../../data/catalog/miyagi_policy_review_manifest.json";

import { aichiPolicyIndicatorStats } from "./aichiIndicators";
import { hiroshimaIndicatorStats } from "./hiroshimaIndicators";
import { hokkaidoIndicatorReviewStats } from "./hokkaidoIndicators";
import { kagawaIndicatorStats } from "./kagawaIndicators";
import { miyagiKpiActualStats } from "./miyagiActuals";
import { miyagiPolicyReviewStats } from "./miyagiPolicies";
import {
  nationwidePrefectureCoverage,
  type PrefectureRegion,
} from "./nationwideCoverage";
import { okinawaIndicatorStats } from "./okinawaIndicators";
import { osakaIndicatorStats } from "./osakaIndicators";
import { allPolicyTargetStats } from "./policyTargets";
import { tokyoPolicyTargetStats } from "./tokyoPolicyTargets";

export type EvidenceDepthStatus =
  | "not_indexed"
  | "indexed"
  | "reviewed"
  | "linked";

export type EvidenceDepth = {
  target_statements: EvidenceDepthStatus;
  annual_evaluation: EvidenceDepthStatus;
  budget: EvidenceDepthStatus;
  project_evaluation: EvidenceDepthStatus;
  contracts: EvidenceDepthStatus;
};

export type ReviewProfile =
  | "actuals_linked"
  | "finance_reviewed"
  | "dedicated_review"
  | "target_statements";

type Phase9Record = {
  prefecture_code: string;
  name: string;
  plan_title: string;
  plan_period: string;
  source_url: string;
  reviewed_target_statement_count: number;
  evidence_packet_count: number;
  document_count: number;
  extraction_error_count: number;
  route: string;
};

type Phase9Summary = {
  prefecture_count: number;
  reviewed_target_statement_count: number;
  evidence_packet_count: number;
  evidence_coverage_percent: number;
  policy_achievement_assessed_count: number;
  ranking_eligible_record_count: number;
  records: Phase9Record[];
  updated_at: string;
};

type Phase10QueueRecord = {
  prefecture_code: string;
  current_depth: EvidenceDepth;
  next_action: string;
};

type Phase10Queue = {
  default_depth: EvidenceDepth;
  wave1_records: Phase10QueueRecord[];
  updated_at: string;
};

type Phase10Completion = {
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
  updated_at: string;
};

type AnchorProfile = {
  reviewedRecords: number;
  evidencePackets: number;
  recordLabel: string;
  profile: Exclude<ReviewProfile, "target_statements">;
};

const phase9Summary = phase9SummaryJson as Phase9Summary;
const phase10Queue = phase10QueueJson as Phase10Queue;
const phase10Completion = phase10CompletionJson as Phase10Completion;

const phase9ByCode = new Map(
  phase9Summary.records.map((record) => [record.prefecture_code, record]),
);
const phase10ByCode = new Map(
  phase10Queue.wave1_records.map((record) => [
    record.prefecture_code,
    record,
  ]),
);

const anchorProfiles: Record<string, AnchorProfile> = {
  "01": {
    reviewedRecords: hokkaidoIndicatorReviewStats.reviewedIndicators,
    evidencePackets: hokkaidoIndicatorReviewStats.evidencePackets,
    recordLabel: "政策指標",
    profile: "dedicated_review",
  },
  "04": {
    reviewedRecords: miyagiPolicyReviewStats.reviewedTargetGroups,
    evidencePackets: miyagiPolicyReviewStats.kpiEvidencePackets,
    recordLabel: "目標グループ",
    profile: "actuals_linked",
  },
  "13": {
    reviewedRecords: tokyoPolicyTargetStats.reviewedTargetCards,
    evidencePackets: tokyoPolicyTargetStats.evidencePackets,
    recordLabel: "目標カード",
    profile: "dedicated_review",
  },
  "23": {
    reviewedRecords: aichiPolicyIndicatorStats.indicatorRows,
    evidencePackets: aichiPolicyIndicatorStats.evidencePackets,
    recordLabel: "進捗指標",
    profile: "dedicated_review",
  },
  "27": {
    reviewedRecords: osakaIndicatorStats.indicatorRows,
    evidencePackets: osakaIndicatorStats.evidencePackets,
    recordLabel: "戦略指標",
    profile: "dedicated_review",
  },
  "34": {
    reviewedRecords: hiroshimaIndicatorStats.reviewedIndicators,
    evidencePackets: hiroshimaIndicatorStats.evidencePackets,
    recordLabel: "成果指標",
    profile: "dedicated_review",
  },
  "37": {
    reviewedRecords: kagawaIndicatorStats.reviewedIndicators,
    evidencePackets: kagawaIndicatorStats.evidencePackets,
    recordLabel: "計画指標",
    profile: "dedicated_review",
  },
  "40": {
    reviewedRecords: allPolicyTargetStats.reviewedTargets,
    evidencePackets: allPolicyTargetStats.reviewedTargets,
    recordLabel: "数値目標",
    profile: "finance_reviewed",
  },
  "47": {
    reviewedRecords: okinawaIndicatorStats.reviewedIndicators,
    evidencePackets: okinawaIndicatorStats.evidencePackets,
    recordLabel: "中期計画指標",
    profile: "dedicated_review",
  },
};

export const evidenceDepthLabels: Record<keyof EvidenceDepth, string> = {
  target_statements: "目標",
  annual_evaluation: "実績",
  budget: "予算",
  project_evaluation: "事業",
  contracts: "契約",
};

export const evidenceDepthOrder = Object.keys(
  evidenceDepthLabels,
) as Array<keyof EvidenceDepth>;

export const evidenceDepthStatusLabels: Record<EvidenceDepthStatus, string> = {
  not_indexed: "未索引",
  indexed: "索引済",
  reviewed: "照合済",
  linked: "接続済",
};

export const reviewProfileLabels: Record<ReviewProfile, string> = {
  actuals_linked: "年度実績まで接続",
  finance_reviewed: "財政値を照合",
  dedicated_review: "専用分析",
  target_statements: "目標原文",
};

function depthForPrefecture(code: string): EvidenceDepth {
  return (
    phase10ByCode.get(code)?.current_depth ?? phase10Queue.default_depth
  );
}

function nextActionForPrefecture(code: string) {
  return (
    phase10ByCode.get(code)?.next_action ??
    "年度評価、予算、重点事業、契約の公式資料入口を索引化し、目標との接続候補を作る。"
  );
}

export const reviewedPrefectureCoverage = nationwidePrefectureCoverage.map(
  (record) => {
    const phase9Record = phase9ByCode.get(record.prefecture_code);
    const anchor = anchorProfiles[record.prefecture_code];

    if (!phase9Record && !anchor) {
      throw new Error(
        `Reviewed coverage is missing for ${record.prefecture_code} ${record.name}`,
      );
    }

    return {
      code: record.prefecture_code,
      name: record.name,
      region: record.region as PrefectureRegion,
      officialUrl: record.official_url,
      route:
        phase9Record?.route ??
        record.publicHref ??
        `/municipalities/${record.slug}`,
      planTitle:
        phase9Record?.plan_title ??
        record.planSource?.title ??
        "現行政策計画",
      planPeriod: phase9Record?.plan_period ?? null,
      planUrl:
        phase9Record?.source_url ??
        record.planSource?.url ??
        record.official_url,
      reviewedRecords:
        phase9Record?.reviewed_target_statement_count ??
        (anchor as AnchorProfile).reviewedRecords,
      evidencePackets:
        phase9Record?.evidence_packet_count ??
        (anchor as AnchorProfile).evidencePackets,
      recordLabel:
        phase9Record ? "目標原文" : (anchor as AnchorProfile).recordLabel,
      reviewProfile:
        phase9Record?.reviewed_target_statement_count !== undefined
          ? ("target_statements" as const)
          : (anchor as AnchorProfile).profile,
      depth: depthForPrefecture(record.prefecture_code),
      nextAction: nextActionForPrefecture(record.prefecture_code),
      extractionErrors: phase9Record?.extraction_error_count ?? 0,
      sourceDocuments: phase9Record?.document_count ?? null,
      dedicatedPage: !phase9Record,
    };
  },
);

const anchorReviewedRecords = Object.values(anchorProfiles).reduce(
  (total, profile) => total + profile.reviewedRecords,
  0,
);
const anchorEvidencePackets = Object.values(anchorProfiles).reduce(
  (total, profile) => total + profile.evidencePackets,
  0,
);
const phase9SourceDocuments = phase9Summary.records.reduce(
  (total, record) => total + record.document_count,
  0,
);
const phase9ExtractionErrors = phase9Summary.records.reduce(
  (total, record) => total + record.extraction_error_count,
  0,
);

const latestDataDate = [
  phase9Summary.updated_at,
  phase10Queue.updated_at,
  phase10Completion.updated_at,
  miyagiReviewManifestJson.updated_at,
].sort().at(-1) as string;

function countDepth(
  key: keyof EvidenceDepth,
  statuses: EvidenceDepthStatus[],
) {
  return reviewedPrefectureCoverage.filter((record) =>
    statuses.includes(record.depth[key]),
  ).length;
}

export const reviewedCoverageStats = {
  totalPrefectures: reviewedPrefectureCoverage.length,
  publishedPrefectures: reviewedPrefectureCoverage.length,
  reviewedPrefectures: reviewedPrefectureCoverage.length,
  reviewedRecords:
    phase9Summary.reviewed_target_statement_count + anchorReviewedRecords,
  evidencePackets:
    phase9Summary.evidence_packet_count + anchorEvidencePackets,
  evidenceCoveragePercent: Math.round(
    ((phase9Summary.evidence_packet_count + anchorEvidencePackets) /
      (phase9Summary.reviewed_target_statement_count + anchorReviewedRecords)) *
      100,
  ),
  dedicatedPrefectures: Object.keys(anchorProfiles).length,
  phase9Prefectures: phase9Summary.prefecture_count,
  anchorReviewedRecords,
  phase9ReviewedRecords: phase9Summary.reviewed_target_statement_count,
  phase9SourceDocuments,
  phase9ExtractionErrors,
  annualResultRows: miyagiKpiActualStats.annualResultRows,
  linkedAnnualSeries: miyagiKpiActualStats.linkedSeries,
  reviewNeededAnnualSeries: miyagiKpiActualStats.reviewNeededSeries,
  policyAssessments: phase9Summary.policy_achievement_assessed_count,
  rankingEligibleRecords: phase9Summary.ranking_eligible_record_count,
  targetReviewedPrefectures:
    phase10Completion.counts.target_statements_reviewed,
  annualLinkedPrefectures: countDepth("annual_evaluation", ["linked"]),
  annualIndexedOrBetterPrefectures: countDepth("annual_evaluation", [
    "indexed",
    "reviewed",
    "linked",
  ]),
  budgetReviewedPrefectures: countDepth("budget", ["reviewed", "linked"]),
  budgetIndexedOrBetterPrefectures: countDepth("budget", [
    "indexed",
    "reviewed",
    "linked",
  ]),
  projectIndexedOrBetterPrefectures: countDepth("project_evaluation", [
    "indexed",
    "reviewed",
    "linked",
  ]),
  contractIndexedOrBetterPrefectures: countDepth("contracts", [
    "indexed",
    "reviewed",
    "linked",
  ]),
  updatedAt: latestDataDate,
};

export const phase10StageSummary = [
  {
    key: "target_statements" as const,
    label: "目標",
    count: reviewedCoverageStats.targetReviewedPrefectures,
    note: "47都道府県でReviewed",
  },
  {
    key: "annual_evaluation" as const,
    label: "実績",
    count: reviewedCoverageStats.annualIndexedOrBetterPrefectures,
    note: `${reviewedCoverageStats.annualLinkedPrefectures}接続・${reviewedCoverageStats.annualIndexedOrBetterPrefectures - reviewedCoverageStats.annualLinkedPrefectures}索引`,
  },
  {
    key: "budget" as const,
    label: "予算",
    count: reviewedCoverageStats.budgetIndexedOrBetterPrefectures,
    note: `${reviewedCoverageStats.budgetReviewedPrefectures}照合・${reviewedCoverageStats.budgetIndexedOrBetterPrefectures - reviewedCoverageStats.budgetReviewedPrefectures}索引`,
  },
  {
    key: "project_evaluation" as const,
    label: "事業",
    count: reviewedCoverageStats.projectIndexedOrBetterPrefectures,
    note: "2都道府県で入口を索引",
  },
  {
    key: "contracts" as const,
    label: "契約",
    count: reviewedCoverageStats.contractIndexedOrBetterPrefectures,
    note: "2都道府県で入口を索引",
  },
];
