import coverageRegistry from "../../../data/catalog/prefecture_coverage.json";
import sourceInventoryRegistry from "../../../data/catalog/nationwide_source_inventory.json";

export type PrefectureRegion =
  | "北海道"
  | "東北"
  | "関東"
  | "中部"
  | "近畿"
  | "中国"
  | "四国"
  | "九州・沖縄";

export type CoverageStage =
  | "registered"
  | "official_entry_verified"
  | "source_cataloged"
  | "reviewed_data";

export type PlanReviewStatus = "not_started" | "indexed" | "reviewed" | "verified";
export type PlanCurrencyStatus =
  | "not_started"
  | "current_unconfirmed"
  | "current_confirmed";
export type PlanSourceKind =
  | "comprehensive_plan"
  | "long_term_vision"
  | "regional_strategy"
  | "annual_policy_portfolio"
  | "governance_framework"
  | "plan_index";
export type SourceInventoryCategory =
  | "policy_plan"
  | "implementation_plan"
  | "kpi_source"
  | "annual_evaluation"
  | "budget"
  | "project_evaluation";
export type SourceInventoryStatus =
  | "not_indexed"
  | "indexed"
  | "reviewed"
  | "linked";

export type PrefectureCoverageRecord = {
  prefecture_code: string;
  entity_id: string;
  slug: string;
  name: string;
  region: PrefectureRegion;
  government_type: "都" | "道" | "府" | "県";
  official_url: string;
};

export type PrefecturePlanSource = {
  prefecture_code: string;
  title: string;
  url: string;
  source_kind: PlanSourceKind;
  plan_status: "current_confirmed" | "current_review_required";
  review_status: Exclude<PlanReviewStatus, "not_started">;
  verified_at: string;
};

export type PrefectureSourceInventoryRecord = {
  prefecture_code: string;
  sources: Record<SourceInventoryCategory, SourceInventoryStatus>;
  next_action: string;
};

type SourceStatusCounts = Record<SourceInventoryStatus, number>;

const records = coverageRegistry.records as PrefectureCoverageRecord[];
const verifiedOfficialCodes = new Set(coverageRegistry.verified_official_codes);
const regionalAnchorCodes = new Set(coverageRegistry.regional_anchor_codes);
const reviewedPrefectureCodes = new Set(coverageRegistry.reviewed_prefecture_codes);
const currentPlanConfirmedCodes = new Set(
  coverageRegistry.current_plan_confirmed_codes,
);
const planSources = coverageRegistry.plan_sources as PrefecturePlanSource[];
const planSourcesByCode = new Map(
  planSources.map((source) => [source.prefecture_code, source]),
);

export const regionOrder: PrefectureRegion[] = [
  "北海道",
  "東北",
  "関東",
  "中部",
  "近畿",
  "中国",
  "四国",
  "九州・沖縄",
];

export const nationwidePrefectureCoverage = records.map((record) => {
  const planSource = planSourcesByCode.get(record.prefecture_code) ?? null;
  const officialEntryVerified = verifiedOfficialCodes.has(record.prefecture_code);
  const reviewed = reviewedPrefectureCodes.has(record.prefecture_code);
  const planCurrencyStatus: PlanCurrencyStatus = currentPlanConfirmedCodes.has(
    record.prefecture_code,
  )
    ? "current_confirmed"
    : planSource
      ? "current_unconfirmed"
      : "not_started";
  const coverageStage: CoverageStage = reviewed
    ? "reviewed_data"
    : planSource
      ? "source_cataloged"
      : officialEntryVerified
        ? "official_entry_verified"
        : "registered";

  return {
    ...record,
    officialEntryStatus: officialEntryVerified
      ? ("verified" as const)
      : ("candidate" as const),
    planSource,
    planReviewStatus: planSource?.review_status ?? ("not_started" as const),
    planCurrencyStatus,
    coverageStage,
    expansionWave: regionalAnchorCodes.has(record.prefecture_code)
      ? ("wave_1_regional_anchor" as const)
      : ("wave_2_nationwide_followup" as const),
    publicHref:
      record.prefecture_code === "01"
        ? "/municipalities/hokkaido"
        : record.prefecture_code === "04"
          ? "/municipalities/miyagi"
          : record.prefecture_code === "40"
            ? "/municipalities/fukuoka-prefecture"
            : null,
  };
});

export const nationwideCoverageStats = {
  totalPrefectures: nationwidePrefectureCoverage.length,
  verifiedOfficialEntries: nationwidePrefectureCoverage.filter(
    (record) => record.officialEntryStatus === "verified",
  ).length,
  indexedPlanSources: planSources.filter(
    (source) => source.review_status === "indexed",
  ).length,
  reviewedPlanSources: planSources.filter(
    (source) =>
      source.review_status === "reviewed" || source.review_status === "verified",
  ).length,
  sourceCatalogedPrefectures: nationwidePrefectureCoverage.filter(
    (record) =>
      record.coverageStage === "source_cataloged" ||
      record.coverageStage === "reviewed_data",
  ).length,
  currentPlanConfirmedPrefectures: nationwidePrefectureCoverage.filter(
    (record) => record.planCurrencyStatus === "current_confirmed",
  ).length,
  currentPlanUnconfirmedPrefectures: nationwidePrefectureCoverage.filter(
    (record) => record.planCurrencyStatus === "current_unconfirmed",
  ).length,
  reviewedPrefectures: nationwidePrefectureCoverage.filter(
    (record) => record.coverageStage === "reviewed_data",
  ).length,
  publishedPrefecturePages: nationwidePrefectureCoverage.filter(
    (record) => record.publicHref !== null,
  ).length,
  candidateOfficialEntries: nationwidePrefectureCoverage.filter(
    (record) => record.officialEntryStatus === "candidate",
  ).length,
  updatedAt: coverageRegistry.updated_at,
};

export const nationwideSourceInventory =
  sourceInventoryRegistry.records as PrefectureSourceInventoryRecord[];

const sourceInventorySummary = sourceInventoryRegistry.summary as Record<
  SourceInventoryCategory,
  SourceStatusCounts
>;

export const sourceInventoryCategoryOrder =
  sourceInventoryRegistry.categories as SourceInventoryCategory[];

export const nationwideSourceInventoryStats = Object.fromEntries(
  sourceInventoryCategoryOrder.map((category) => {
    const counts = sourceInventorySummary[category];
    return [
      category,
      {
        ...counts,
        indexedOrHigher: counts.indexed + counts.reviewed + counts.linked,
        reviewedOrHigher: counts.reviewed + counts.linked,
      },
    ];
  }),
) as Record<
  SourceInventoryCategory,
  SourceStatusCounts & { indexedOrHigher: number; reviewedOrHigher: number }
>;

export const nationwideSourceInventoryByCode = new Map(
  nationwideSourceInventory.map((record) => [record.prefecture_code, record]),
);

export const nationwideCoverageByRegion = regionOrder.map((region) => ({
  region,
  records: nationwidePrefectureCoverage.filter((record) => record.region === region),
}));

export function coverageStageLabel(stage: CoverageStage) {
  const labels: Record<CoverageStage, string> = {
    registered: "全国登録済み",
    official_entry_verified: "公式入口確認済み",
    source_cataloged: "計画資料索引済み",
    reviewed_data: "Reviewedデータ公開",
  };
  return labels[stage];
}

export function coverageStageTone(stage: CoverageStage) {
  if (stage === "reviewed_data") return "verified" as const;
  if (stage === "source_cataloged" || stage === "official_entry_verified") {
    return "progress" as const;
  }
  return "neutral" as const;
}

export function planCurrencyLabel(status: PlanCurrencyStatus) {
  const labels: Record<PlanCurrencyStatus, string> = {
    not_started: "未確認",
    current_unconfirmed: "現行性未確認",
    current_confirmed: "現行計画確認済み",
  };
  return labels[status];
}

export function sourceInventoryCategoryLabel(category: SourceInventoryCategory) {
  const labels: Record<SourceInventoryCategory, string> = {
    policy_plan: "政策計画",
    implementation_plan: "実施計画",
    kpi_source: "KPI・数値目標",
    annual_evaluation: "年度評価",
    budget: "予算・決算",
    project_evaluation: "事業評価",
  };
  return labels[category];
}
