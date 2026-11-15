import fs from "node:fs";
import path from "node:path";

import phase15QueueJson from "../../../data/catalog/phase15_core_capital_review_queue.json";

/**
 * Public, read-only Phase 15 city detail data.
 *
 * Pages are driven exclusively by the canonical review queue plus each city's
 * reviewed_complete completion record. The reviewed package files are read
 * from disk (the phase9Targets pattern) instead of being bundled. Any
 * inconsistency between the queue, the completion record and the package
 * fails the build: an unverified or missing package must never render as a
 * Reviewed city page. Staged candidate files are never read here.
 */

export type Phase15PlanRecord = {
  id: string;
  evidenceRole: string;
  title: string;
  statement: string;
  value: string | number | null;
  unit: string | null;
  fiscalYear: number | null;
  sourceUrl: string;
  evidenceLocation: string;
  decision: string;
  reviewNote: string;
};

export type Phase15ResolvedSource = {
  id: string;
  title: string;
  officialUrl: string;
  format: string | null;
  evidenceRole: string | null;
  evidenceLocation: string | null;
  useBoundary: string | null;
};

export type Phase15FiscalRecord = {
  id: string;
  fiscalYear: number;
  accountType: string;
  stage: string;
  metric: string;
  metricLabel: string;
  amountYen: number | null;
  valueStatus: string;
  periodStart: string;
  periodEnd: string;
  note: string;
  reviewStatus: string;
  sources: Phase15ResolvedSource[];
  claims: Array<{
    field: string;
    statement: string;
    locationNote: string;
    decision: string;
    reviewNote: string;
    sources: Phase15ResolvedSource[];
  }>;
  openQuestions: string[];
};

export type Phase15City = {
  slug: string;
  officialCode: string;
  name: string;
  prefecture: string;
  municipalityType: string;
  officialUrl: string;
  lastVerifiedAt: string;
  reviewedAt: string;
  completedAt: string;
  completionPath: string;
  completionBoundary: string;
  qualityBoundary: string;
  nextAction: string;
  deferredDepth: Array<{ id: string; status: string; boundary: string }>;
  planRecords: Phase15PlanRecord[];
  fiscalRecords: Phase15FiscalRecord[];
  sources: Phase15ResolvedSource[];
  packagePaths: {
    municipality: string;
    planReview: string;
    fiscalRecords: string;
    evidencePackets: string;
    sourceCatalog: string;
  };
};

export type Phase15CitySummary = {
  slug: string;
  officialCode: string;
  name: string;
  prefecture: string;
  completedAt: string;
};

type QueueItem = {
  official_code: string;
  name_ja: string;
  prefecture_name_ja: string;
  status: string;
  completion_path: string | null;
};

type RawMunicipality = {
  official_code: string;
  name_ja: string;
  municipality_type: string;
  prefecture_name_ja: string;
  official_url: string;
  data_status: string;
  last_verified_at: string;
  sources: string[];
};

type RawPlanReview = {
  review_status: string;
  reviewed_at: string;
  records: Array<{
    id: string;
    evidence_role: string;
    title: string;
    statement: string;
    value?: string | number | null;
    unit?: string | null;
    fiscal_year?: number | null;
    source_url: string;
    evidence_location: string;
    decision: string;
    review_note: string;
  }>;
  quality_boundary: string;
  next_action: string;
};

type RawFiscalRecord = {
  id: string;
  fiscal_year: number;
  account_type: string;
  stage: string;
  metric: string;
  metric_label: string;
  amount_yen: number | null;
  value_status: string;
  period_start: string;
  period_end: string;
  note: string;
  review_status: string;
  sources: string[];
};

type RawEvidencePacket = {
  subject_id: string;
  claims: Array<{
    field: string;
    statement: string;
    location_note: string;
    decision: string;
    review_note: string;
    source_ids: string[];
  }>;
  open_questions: string[];
};

type RawSource = {
  id: string;
  title: string;
  official_url: string;
  format: string;
  evidence_role: string;
  evidence_location: string;
  use_boundary: string;
};

type RawCompletion = {
  status: string;
  official_code: string;
  completed_at: string;
  review_package: {
    source_catalog_path: string;
    plan_review_path: string;
    fiscal_records_path: string;
    fiscal_evidence_path: string;
  };
  deferred_depth: Array<{ id: string; status: string; boundary: string }>;
  completion_boundary: string;
};

const queue = phase15QueueJson as unknown as {
  execution_queue: QueueItem[];
};

function findDataRoot(): string {
  const candidates = [
    path.resolve(process.cwd(), "data"),
    path.resolve(process.cwd(), "../../data"),
  ];
  return candidates.find((candidate) => fs.existsSync(candidate)) ?? candidates[0];
}

const dataRoot = findDataRoot();
const repoRoot = path.dirname(dataRoot);

function fail(message: string): never {
  throw new Error(`Phase 15 city pages: ${message}`);
}

function readAbsoluteJson<T>(absolutePath: string, context: string): T {
  if (!fs.existsSync(absolutePath)) {
    fail(`${context} is missing at ${absolutePath}. A reviewed_complete city without its package files must fail the build.`);
  }
  return JSON.parse(fs.readFileSync(absolutePath, "utf-8")) as T;
}

/** Read a file addressed relative to the data root, e.g. "catalog/x.json". */
function readJson<T>(relativePath: string, context: string): T {
  return readAbsoluteJson<T>(path.join(dataRoot, relativePath), context);
}

/** Read a file addressed relative to the repository root, e.g. "data/catalog/x.json". */
function readRepoJson<T>(relativePath: string, context: string): T {
  return readAbsoluteJson<T>(path.join(repoRoot, relativePath), context);
}

/** Derive the reviewed directory slug from a completion path, e.g.
 *  data/catalog/morioka_phase15_completion.json -> morioka-city */
export function phase15SlugFromCompletionPath(completionPath: string): string {
  const fileName = completionPath.split("/").pop() ?? "";
  const suffix = "_phase15_completion.json";
  if (!fileName.endsWith(suffix)) {
    fail(`cannot derive a city slug from completion path ${completionPath}.`);
  }
  return `${fileName.slice(0, -suffix.length)}-city`;
}

function loadCity(item: QueueItem): Phase15City {
  if (!item.completion_path) {
    fail(`queue item ${item.official_code} is reviewed_complete without a completion_path.`);
  }
  const completionPath = item.completion_path;
  const slug = phase15SlugFromCompletionPath(completionPath);
  const base = slug.replace(/-city$/, "");
  const completion = readRepoJson<RawCompletion>(completionPath, `completion record for ${slug}`);

  if (completion.status !== "reviewed_complete") {
    fail(`completion record for ${slug} has status ${completion.status}, not reviewed_complete.`);
  }
  if (completion.official_code !== item.official_code) {
    fail(`completion record for ${slug} does not match the queue official_code ${item.official_code}.`);
  }

  const expectedPaths = {
    sourceCatalog: `catalog/${base}_phase15_sources.json`,
    planReview: `reviewed/${slug}/plan_review.json`,
    fiscalRecords: `reviewed/${slug}/fiscal_records.json`,
    evidencePackets: `reviewed/${slug}/evidence_packets.json`,
  };
  const declared = completion.review_package;
  if (
    declared.source_catalog_path !== `data/${expectedPaths.sourceCatalog}` ||
    declared.plan_review_path !== `data/${expectedPaths.planReview}` ||
    declared.fiscal_records_path !== `data/${expectedPaths.fiscalRecords}` ||
    declared.fiscal_evidence_path !== `data/${expectedPaths.evidencePackets}`
  ) {
    fail(`completion record for ${slug} declares package paths that do not match the canonical locations.`);
  }

  const municipalityPath = `reviewed/${slug}/municipality.json`;
  const municipality = readJson<RawMunicipality>(municipalityPath, `municipality record for ${slug}`);
  if (municipality.data_status !== "reviewed") {
    fail(`municipality record for ${slug} has data_status ${municipality.data_status}, not reviewed.`);
  }
  if (municipality.official_code !== item.official_code || municipality.name_ja !== item.name_ja) {
    fail(`municipality record for ${slug} does not match the queue entry ${item.official_code}.`);
  }

  const planReview = readJson<RawPlanReview>(expectedPaths.planReview, `plan review for ${slug}`);
  if (planReview.review_status !== "reviewed") {
    fail(`plan review for ${slug} has review_status ${planReview.review_status}, not reviewed.`);
  }
  for (const record of planReview.records) {
    if (!record.source_url) {
      fail(`plan review record ${record.id} for ${slug} has no source_url.`);
    }
  }

  const sourceCatalog = readJson<{ sources: RawSource[] }>(
    expectedPaths.sourceCatalog,
    `source catalog for ${slug}`,
  );
  const catalogById = new Map(sourceCatalog.sources.map((source) => [source.id, source]));

  // A small number of referenced source ids are catalogued only in the city's
  // finance source inventory (data/catalog/<city>_city_finance_sources.json),
  // not in the Phase 15 source catalog. Those records are canonical too, so
  // they are consulted as a fallback; an id found in neither catalog fails.
  const financeCatalogPath = path.join(dataRoot, "catalog", `${base}_city_finance_sources.json`);
  const financeById = new Map<string, { title: string; url: string }>();
  if (fs.existsSync(financeCatalogPath)) {
    const financeCatalog = readJson<{ records: Array<{ id: string; title: string; url: string }> }>(
      `catalog/${base}_city_finance_sources.json`,
      `finance source catalog for ${slug}`,
    );
    for (const record of financeCatalog.records) {
      financeById.set(record.id, { title: record.title, url: record.url });
    }
  }

  const resolveSource = (sourceId: string): Phase15ResolvedSource => {
    const entry = catalogById.get(sourceId);
    if (entry) {
      return {
        id: entry.id,
        title: entry.title,
        officialUrl: entry.official_url,
        format: entry.format,
        evidenceRole: entry.evidence_role,
        evidenceLocation: entry.evidence_location,
        useBoundary: entry.use_boundary,
      };
    }
    const financeEntry = financeById.get(sourceId);
    if (financeEntry) {
      return {
        id: sourceId,
        title: financeEntry.title,
        officialUrl: financeEntry.url,
        format: null,
        evidenceRole: null,
        evidenceLocation: null,
        useBoundary: null,
      };
    }
    // The one documented exception: "<city>-city-home" is not in the source
    // catalog and points at the municipality's official top page.
    if (sourceId === `${base}-city-home`) {
      return {
        id: sourceId,
        title: `${municipality.name_ja}公式サイト`,
        officialUrl: municipality.official_url,
        format: "html",
        evidenceRole: "municipality_home",
        evidenceLocation: null,
        useBoundary: null,
      };
    }
    return fail(`source id ${sourceId} for ${slug} cannot be resolved from the source catalog.`);
  };

  const fiscalRaw = readJson<RawFiscalRecord[]>(expectedPaths.fiscalRecords, `fiscal records for ${slug}`);
  const packetsRaw = readJson<RawEvidencePacket[]>(expectedPaths.evidencePackets, `evidence packets for ${slug}`);
  const packetsBySubject = new Map(packetsRaw.map((packet) => [packet.subject_id, packet]));

  const fiscalRecords: Phase15FiscalRecord[] = fiscalRaw.map((record) => {
    if (record.review_status !== "reviewed") {
      fail(`fiscal record ${record.id} for ${slug} has review_status ${record.review_status}, not reviewed.`);
    }
    if (record.value_status === "available" && typeof record.amount_yen !== "number") {
      fail(`fiscal record ${record.id} for ${slug} is marked available without an amount.`);
    }
    const packet = packetsBySubject.get(record.id);
    if (!packet) {
      fail(`fiscal record ${record.id} for ${slug} has no matching evidence packet.`);
    }
    return {
      id: record.id,
      fiscalYear: record.fiscal_year,
      accountType: record.account_type,
      stage: record.stage,
      metric: record.metric,
      metricLabel: record.metric_label,
      amountYen: record.amount_yen,
      valueStatus: record.value_status,
      periodStart: record.period_start,
      periodEnd: record.period_end,
      note: record.note,
      reviewStatus: record.review_status,
      sources: record.sources.map(resolveSource),
      claims: packet.claims.map((claim) => ({
        field: claim.field,
        statement: claim.statement,
        locationNote: claim.location_note,
        decision: claim.decision,
        reviewNote: claim.review_note,
        sources: claim.source_ids.map(resolveSource),
      })),
      openQuestions: packet.open_questions,
    };
  });

  // Every source the municipality record lists must also resolve.
  for (const sourceId of municipality.sources) {
    resolveSource(sourceId);
  }

  return {
    slug,
    officialCode: item.official_code,
    name: item.name_ja,
    prefecture: item.prefecture_name_ja,
    municipalityType: municipality.municipality_type,
    officialUrl: municipality.official_url,
    lastVerifiedAt: municipality.last_verified_at,
    reviewedAt: planReview.reviewed_at,
    completedAt: completion.completed_at,
    completionPath,
    completionBoundary: completion.completion_boundary,
    qualityBoundary: planReview.quality_boundary,
    nextAction: planReview.next_action,
    deferredDepth: completion.deferred_depth,
    planRecords: planReview.records.map((record) => ({
      id: record.id,
      evidenceRole: record.evidence_role,
      title: record.title,
      statement: record.statement,
      value: record.value ?? null,
      unit: record.unit ?? null,
      fiscalYear: record.fiscal_year ?? null,
      sourceUrl: record.source_url,
      evidenceLocation: record.evidence_location,
      decision: record.decision,
      reviewNote: record.review_note,
    })),
    fiscalRecords,
    sources: sourceCatalog.sources.map((source) => resolveSource(source.id)),
    packagePaths: {
      municipality: `data/${municipalityPath}`,
      planReview: `data/${expectedPaths.planReview}`,
      fiscalRecords: `data/${expectedPaths.fiscalRecords}`,
      evidencePackets: `data/${expectedPaths.evidencePackets}`,
      sourceCatalog: `data/${expectedPaths.sourceCatalog}`,
    },
  };
}

let cachedCities: Phase15City[] | null = null;

export function loadPhase15Cities(): Phase15City[] {
  if (cachedCities) {
    return cachedCities;
  }
  const reviewedItems = queue.execution_queue.filter((item) => item.status === "reviewed_complete");
  cachedCities = reviewedItems.map(loadCity);
  return cachedCities;
}

export function loadPhase15CitySummaries(): Phase15CitySummary[] {
  return loadPhase15Cities().map((city) => ({
    slug: city.slug,
    officialCode: city.officialCode,
    name: city.name,
    prefecture: city.prefecture,
    completedAt: city.completedAt,
  }));
}

export function loadPhase15City(slug: string): Phase15City | null {
  return loadPhase15Cities().find((city) => city.slug === slug) ?? null;
}
