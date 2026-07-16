import policySourceCatalog from "../../../data/catalog/policy_sources.json";

import { sourceCatalog, type MunicipalityKey } from "./catalog";
import {
  currentExecutiveTerms,
  executiveEvidencePackets,
  manifestoReviewRecords,
  manifestoSourceSearchRecords,
} from "./executives";
import { fukuokaPrefectureFinance } from "./finance";
import { fukuokaCityFinance } from "./fukuokaCityFinance";
import { hokkaidoPolicyHierarchyStats } from "./hokkaidoPolicies";
import { kitakyushuFinance } from "./kitakyushuFinance";
import { nationwideCoverageStats } from "./nationwideCoverage";
import { policyDirectionStats, policyInitiativeStats } from "./policies";
import { waveOnePolicyReviewStats } from "./policyReviewQueue";
import { allPolicyTargetStats } from "./policyTargets";
import { sourceRequestRecords } from "./sourceRequests";

export type MunicipalityQuality = {
  key: MunicipalityKey;
  name: string;
  officialSources: number;
  reviewedFiscalValues: number;
  evidencePackets: number;
  publicEvaluations: number;
  status: "reviewed-data" | "indexed-only";
};

const municipalityNames: Record<MunicipalityKey, string> = {
  "fukuoka-prefecture": "福岡県",
  "fukuoka-city": "福岡市",
  "kitakyushu-city": "北九州市",
};

const municipalityKeys = Object.keys(municipalityNames) as MunicipalityKey[];
const recordsByMunicipality: Record<
  MunicipalityKey,
  typeof fukuokaPrefectureFinance.records
> = {
  "fukuoka-prefecture": fukuokaPrefectureFinance.records,
  "fukuoka-city": fukuokaCityFinance.records,
  "kitakyushu-city": kitakyushuFinance.records,
};
const evidenceByMunicipality: Record<
  MunicipalityKey,
  typeof fukuokaPrefectureFinance.evidencePackets
> = {
  "fukuoka-prefecture": fukuokaPrefectureFinance.evidencePackets,
  "fukuoka-city": fukuokaCityFinance.evidencePackets,
  "kitakyushu-city": kitakyushuFinance.evidencePackets,
};
const fiscalRecords = Object.values(recordsByMunicipality).flat();
const evidencePackets = Object.values(evidenceByMunicipality).flat();
const evidenceSubjects = new Set(evidencePackets.map((packet) => packet.subject_id));
const policySourceRecords = policySourceCatalog.records;

export const dataQualitySnapshot = {
  updatedAt: "2026-07-16",
  pilotMunicipalities: municipalityKeys.length,
  nationwidePrefectures: nationwideCoverageStats.totalPrefectures,
  verifiedPrefectureOfficialEntries:
    nationwideCoverageStats.verifiedOfficialEntries,
  sourceCatalogedPrefectures: nationwideCoverageStats.sourceCatalogedPrefectures,
  currentPlanConfirmedPrefectures:
    nationwideCoverageStats.currentPlanConfirmedPrefectures,
  currentPlanUnconfirmedPrefectures:
    nationwideCoverageStats.currentPlanUnconfirmedPrefectures,
  reviewedPrefectures: nationwideCoverageStats.reviewedPrefectures,
  publishedPrefecturePages: nationwideCoverageStats.publishedPrefecturePages,
  candidatePrefectureOfficialEntries:
    nationwideCoverageStats.candidateOfficialEntries,
  policySourceRecords: policySourceRecords.length,
  indexedPolicySourceRecords: policySourceRecords.filter(
    (source) => source.collection_status === "indexed",
  ).length,
  reviewedPolicySourceRecords: policySourceRecords.filter(
    (source) => source.review_status === "reviewed",
  ).length,
  waveOnePolicyReviewReferences: waveOnePolicyReviewStats.reviewedReferences,
  waveOnePolicyActiveReviews: waveOnePolicyReviewStats.activeReviews,
  waveOnePolicyQueued: waveOnePolicyReviewStats.queued,
  officialSources: sourceCatalog.length,
  reviewedSources: sourceCatalog.filter(
    (source) =>
      source.review_status === "reviewed" || source.review_status === "verified",
  ).length,
  reviewedFiscalValues: fiscalRecords.filter(
    (record) =>
      record.review_status === "reviewed" || record.review_status === "verified",
  ).length,
  evidencePackets: evidencePackets.length,
  evidenceCoveragePercent:
    fiscalRecords.length === 0
      ? 0
      : Math.round(
          (fiscalRecords.filter((record) => evidenceSubjects.has(record.id)).length /
            fiscalRecords.length) *
            100,
        ),
  initialBudgetValues: fiscalRecords.filter(
    (record) => record.stage === "initial_budget",
  ).length,
  settlementValues: fiscalRecords.filter(
    (record) => record.stage === "settlement",
  ).length,
  reviewedPolicyDirections:
    policyDirectionStats.reviewedDirections +
    hokkaidoPolicyHierarchyStats.reviewedDirections,
  reviewedHokkaidoPolicyDirections:
    hokkaidoPolicyHierarchyStats.reviewedDirections,
  reviewedHokkaidoPolicyFields: hokkaidoPolicyHierarchyStats.reviewedFields,
  hokkaidoPolicyEvidencePackets: hokkaidoPolicyHierarchyStats.evidencePackets,
  hokkaidoIndicatorTarget: hokkaidoPolicyHierarchyStats.indicatorTarget,
  hokkaidoDuplicateInclusiveIndicatorRows:
    hokkaidoPolicyHierarchyStats.duplicateInclusiveIndicatorRows,
  reviewedPolicyInitiatives: policyInitiativeStats.reviewedInitiatives,
  reviewedPolicyTargets: allPolicyTargetStats.reviewedTargets,
  policyTargetsActualsLinked: allPolicyTargetStats.actualsLinked,
  policyInitiativesProgressLinked: policyInitiativeStats.progressLinked,
  assessedPolicyInitiatives: policyInitiativeStats.assessed,
  reviewedExecutiveTerms: currentExecutiveTerms.length,
  executiveEvidencePackets: executiveEvidencePackets.length,
  manifestoSourceSearches: manifestoSourceSearchRecords.length,
  manifestoSourcesNotFound: manifestoSourceSearchRecords.filter(
    (search) => search.result_status === "no_stable_primary_source_found",
  ).length,
  registeredManifestos: currentExecutiveTerms.filter(
    (term) => term.manifesto_source_ids.length > 0,
  ).length,
  manifestoReviews: manifestoReviewRecords.length,
  extractedPromiseRecords: manifestoReviewRecords.reduce(
    (total, review) => total + review.promise_records_created,
    0,
  ),
  sourceRequestDrafts: sourceRequestRecords.filter(
    (request) => request.status === "draft" || request.status === "ready_for_review",
  ).length,
  sourceRequestsSent: sourceRequestRecords.filter(
    (request) => request.sent_at !== null,
  ).length,
  sourceRequestResponses: sourceRequestRecords.filter(
    (request) => request.response_received_at !== null,
  ).length,
  publicEvaluations: 0,
};

export const municipalityQuality: MunicipalityQuality[] = municipalityKeys.map(
  (key) => {
    const records = recordsByMunicipality[key];
    const packets = evidenceByMunicipality[key];
    return {
      key,
      name: municipalityNames[key],
      officialSources: sourceCatalog.filter(
        (source) => source.municipality_key === key,
      ).length,
      reviewedFiscalValues: records.length,
      evidencePackets: packets.length,
      publicEvaluations: 0,
      status: records.length > 0 ? "reviewed-data" : "indexed-only",
    };
  },
);

export const publicationGaps = [
  "事業別の予算・契約・執行・決算",
  "KPIの年度実績と公式説明",
  "公約原文と事業の根拠付き対応付け",
  "議会の議案・採決・修正・監視活動",
  "類似自治体比較と外部要因の検討",
];
