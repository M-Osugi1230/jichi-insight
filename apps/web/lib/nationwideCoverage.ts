import coverageRegistry from "../../../data/catalog/prefecture_coverage.json";

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
  review_status: Exclude<PlanReviewStatus, "not_started">;
  verified_at: string;
};

const records = coverageRegistry.records as PrefectureCoverageRecord[];
const verifiedOfficialCodes = new Set(coverageRegistry.verified_official_codes);
const regionalAnchorCodes = new Set(coverageRegistry.regional_anchor_codes);
const reviewedPrefectureCodes = new Set(coverageRegistry.reviewed_prefecture_codes);
const planSources = coverageRegistry.plan_sources as PrefecturePlanSource[];
const planSourcesByCode = new Map(planSources.map((source) => [source.prefecture_code, source]));

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
  const coverageStage: CoverageStage = reviewed
    ? "reviewed_data"
    : planSource
      ? "source_cataloged"
      : officialEntryVerified
        ? "official_entry_verified"
        : "registered";

  return {
    ...record,
    officialEntryStatus: officialEntryVerified ? ("verified" as const) : ("candidate" as const),
    planSource,
    planReviewStatus: planSource?.review_status ?? ("not_started" as const),
    coverageStage,
    expansionWave: regionalAnchorCodes.has(record.prefecture_code)
      ? ("wave_1_regional_anchor" as const)
      : ("wave_2_nationwide_followup" as const),
    publicHref: record.prefecture_code === "40" ? "/municipalities/fukuoka-prefecture" : null,
  };
});

export const nationwideCoverageStats = {
  totalPrefectures: nationwidePrefectureCoverage.length,
  verifiedOfficialEntries: nationwidePrefectureCoverage.filter(
    (record) => record.officialEntryStatus === "verified",
  ).length,
  indexedPlanSources: planSources.filter((source) => source.review_status === "indexed").length,
  reviewedPlanSources: planSources.filter(
    (source) => source.review_status === "reviewed" || source.review_status === "verified",
  ).length,
  sourceCatalogedPrefectures: nationwidePrefectureCoverage.filter(
    (record) => record.coverageStage === "source_cataloged" || record.coverageStage === "reviewed_data",
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
