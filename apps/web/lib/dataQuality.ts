import { sourceCatalog, type MunicipalityKey } from "./catalog";
import { currentExecutiveTerms, executiveEvidencePackets } from "./executives";
import { fukuokaPrefectureFinance } from "./finance";
import { fukuokaCityFinance } from "./fukuokaCityFinance";
import { kitakyushuFinance } from "./kitakyushuFinance";

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
const recordsByMunicipality: Record<MunicipalityKey, typeof fukuokaPrefectureFinance.records> = {
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

export const dataQualitySnapshot = {
  updatedAt: "2026-07-15",
  pilotMunicipalities: municipalityKeys.length,
  officialSources: sourceCatalog.length,
  reviewedSources: sourceCatalog.filter(
    (source) => source.review_status === "reviewed" || source.review_status === "verified",
  ).length,
  reviewedFiscalValues: fiscalRecords.filter(
    (record) => record.review_status === "reviewed" || record.review_status === "verified",
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
  initialBudgetValues: fiscalRecords.filter((record) => record.stage === "initial_budget").length,
  settlementValues: fiscalRecords.filter((record) => record.stage === "settlement").length,
  reviewedExecutiveTerms: currentExecutiveTerms.length,
  executiveEvidencePackets: executiveEvidencePackets.length,
  registeredManifestos: currentExecutiveTerms.filter(
    (term) => term.manifesto_source_ids.length > 0,
  ).length,
  publicEvaluations: 0,
};

export const municipalityQuality: MunicipalityQuality[] = municipalityKeys.map((key) => {
  const records = recordsByMunicipality[key];
  const packets = evidenceByMunicipality[key];
  return {
    key,
    name: municipalityNames[key],
    officialSources: sourceCatalog.filter((source) => source.municipality_key === key).length,
    reviewedFiscalValues: records.length,
    evidencePackets: packets.length,
    publicEvaluations: 0,
    status: records.length > 0 ? "reviewed-data" : "indexed-only",
  };
});

export const publicationGaps = [
  "事業別の予算・契約・執行・決算",
  "KPIの基準値・目標・実績",
  "公約原文と事業の根拠付き対応付け",
  "議会の議案・採決・修正・監視活動",
  "類似自治体比較と外部要因の検討",
];
