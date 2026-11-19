import fs from "node:fs";
import path from "node:path";

import { loadPhase15City } from "@/lib/phase15Cities";
import type { EvidencePacket, FiscalRecord } from "@/lib/finance";

export type GenericFiscalSource = {
  id: string;
  title: string;
  url: string;
  indexed_at: string;
};

export type GenericCityFinance = {
  municipality: { id: string; official_code: string; name_ja: string; data_status: string };
  records: FiscalRecord[];
  evidencePackets: EvidencePacket[];
  sources: GenericFiscalSource[];
};

type Municipality = GenericCityFinance["municipality"];
type RawCatalog = { sources: Array<{ id: string; title: string; official_url: string }> };
type FinanceCatalog = { records: Array<{ id: string; title: string; url: string; indexed_at?: string }> };

const dataRoots = [
  path.resolve(process.cwd(), "data"),
  path.resolve(process.cwd(), "../../data"),
];
const dataRoot = dataRoots.find((candidate) => fs.existsSync(candidate)) ?? dataRoots[0];

function readJson<T>(file: string): T {
  return JSON.parse(fs.readFileSync(file, "utf-8")) as T;
}

/** Only an existing Reviewed city may opt into the generic fiscal detail. */
export function loadGenericCityFinance(slug: string): GenericCityFinance | null {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) return null;
  const city = loadPhase15City(slug);
  if (!city) return null;

  const root = path.join(dataRoot, "reviewed", slug);
  const settlementPath = path.join(root, "settlement_records.json");
  // This is an optional, future data package. Do not change legacy pages.
  if (!fs.existsSync(settlementPath)) return null;

  const municipality = readJson<Municipality>(path.join(root, "municipality.json"));
  if (
    municipality.data_status !== "reviewed" ||
    municipality.official_code !== city.officialCode ||
    municipality.id !== `jp-local-${city.officialCode}`
  ) {
    throw new Error(`Generic fiscal detail: municipality identity is not Reviewed for ${slug}`);
  }

  const fiscal = readJson<FiscalRecord[]>(path.join(root, "fiscal_records.json"));
  const settlement = readJson<FiscalRecord[]>(settlementPath);
  const evidencePath = path.join(root, "evidence_packets.json");
  const settlementEvidencePath = path.join(root, "settlement_evidence_packets.json");

  if (!fs.existsSync(settlementEvidencePath)) {
    throw new Error(`Generic fiscal detail: settlement evidence is missing for ${slug}`);
  }

  const evidencePackets = [
    ...readJson<EvidencePacket[]>(evidencePath),
    ...readJson<EvidencePacket[]>(settlementEvidencePath),
  ];
  const evidenceSubjects = new Set(evidencePackets.filter(
    (packet) => packet.review_status === "reviewed" || packet.review_status === "verified",
  ).map((packet) => packet.subject_id));

  const combined = [...fiscal, ...settlement];
  const records = combined.filter((record) =>
    record.review_status === "reviewed" && record.municipality_id === municipality.id,
  );
  if (records.length !== combined.length) {
    throw new Error(`Generic fiscal detail: unreviewed or mismatched record for ${slug}`);
  }
  if (settlement.some((record) =>
    record.review_status !== "reviewed" ||
    record.municipality_id !== municipality.id ||
    record.stage !== "settlement" ||
    record.account_type !== "ordinary" ||
    !evidenceSubjects.has(record.id)
  )) {
    throw new Error(`Generic fiscal detail: settlement must be Reviewed ordinary-account records with evidence for ${slug}`);
  }
  // A file with no Reviewed ordinary-account settlement data is not a usable
  // fiscal detail, and must not activate a navigation link.
  if (settlement.length === 0) return null;

  const base = slug.replace(/-city$/, "");
  const catalogPath = path.join(dataRoot, "catalog", `${base}_phase15_sources.json`);
  const catalog = readJson<RawCatalog>(catalogPath);
  const indexedAt = city.lastVerifiedAt;
  const sources: GenericFiscalSource[] = catalog.sources.map((source) => ({
    id: source.id, title: source.title, url: source.official_url, indexed_at: indexedAt,
  }));
  const financeCatalogPath = path.join(dataRoot, "catalog", `${base}_city_finance_sources.json`);
  if (fs.existsSync(financeCatalogPath)) {
    const more = readJson<FinanceCatalog>(financeCatalogPath).records;
    for (const source of more) {
      if (!sources.some((existing) => existing.id === source.id)) {
        sources.push({ id: source.id, title: source.title, url: source.url, indexed_at: source.indexed_at ?? indexedAt });
      }
    }
  }

  // The default three-city catalog does not cover the generic 68-city
  // sources; keep them local to this FiscalReview instead of global mutation.
  return { municipality, records, evidencePackets, sources };
}
