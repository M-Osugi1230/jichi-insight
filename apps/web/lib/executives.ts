import executiveCatalog from "../../../data/catalog/executive_sources.json";
import evidencePackets from "../../../data/entities/executives/evidence_packets.json";
import executiveTerms from "../../../data/entities/executives/executive_terms.json";
import manifestoReviewPackets from "../../../data/entities/executives/manifesto_review_evidence_packets.json";
import manifestoReviews from "../../../data/entities/executives/manifesto_reviews.json";
import manifestoSourceSearchPackets from "../../../data/entities/executives/manifesto_source_search_evidence_packets.json";
import manifestoSourceSearches from "../../../data/entities/executives/manifesto_source_searches.json";
import promisePackets from "../../../data/entities/executives/promise_evidence_packets.json";
import promises from "../../../data/entities/executives/promises.json";

import { municipalityMeta, sourceCatalog, type SourceRecord } from "./catalog";

export type ExecutiveTerm = {
  id: string;
  municipality_id: string;
  office: "governor" | "mayor";
  person_name: string;
  term_start: string;
  term_end: string | null;
  election_date: string | null;
  status: "current" | "completed" | "resigned" | "vacant";
  manifesto_source_ids: string[];
  review_status: "verified" | "reviewed" | "extracted" | "inferred" | "missing";
  confidence: "high" | "medium" | "low" | "not_assessable";
  sources: string[];
};

export type EvidenceClaim = {
  field: string;
  statement: string;
  source_ids: string[];
  location_note: string | null;
  decision: "accepted" | "rejected" | "needs_review" | "not_assessable";
  review_note: string | null;
};

export type ExecutiveEvidencePacket = {
  id: string;
  subject_type: "executive_term";
  subject_id: string;
  claims: EvidenceClaim[];
  open_questions: string[];
  review_status: "reviewed" | "verified";
};

export type ManifestoReview = {
  id: string;
  executive_term_id: string;
  source_id: string;
  candidate_name: string;
  source_location: string;
  review_scope: "document" | "candidate_panel" | "section";
  statement_boundary: "clear" | "mixed" | "unclear";
  segmentation_status: "segmented" | "manual_review_required" | "not_segmented";
  promise_records_created: number;
  reason_codes: string[];
  review_note: string | null;
  last_reviewed_at: string;
  review_status: "reviewed" | "verified";
  confidence: "high" | "medium" | "low" | "not_assessable";
};

export type ManifestoReviewEvidencePacket = {
  id: string;
  subject_type: "manifesto_review";
  subject_id: string;
  claims: EvidenceClaim[];
  open_questions: string[];
  review_status: "reviewed" | "verified";
};

export type ManifestoSourceSearch = {
  id: string;
  executive_term_id: string;
  searched_at: string;
  search_scopes: Array<
    | "official_election_result_page"
    | "official_site_search"
    | "official_document_archive"
    | "candidate_publication_search"
    | "general_web_search"
  >;
  result_status:
    | "source_registered"
    | "official_result_only"
    | "no_stable_primary_source_found"
    | "follow_up_required";
  manifesto_source_ids_found: string[];
  checked_source_ids: string[];
  nonexistence_claim: false;
  review_note: string;
  next_actions: string[];
  review_status: "reviewed" | "verified";
  confidence: "high" | "medium" | "low" | "not_assessable";
};

export type ManifestoSourceSearchEvidencePacket = {
  id: string;
  subject_type: "manifesto_source_search";
  subject_id: string;
  claims: EvidenceClaim[];
  open_questions: string[];
  review_status: "reviewed" | "verified";
};

const municipalityIdToKey = {
  "jp-local-431001": "kumamoto-city",
  "jp-local-150002": "niigata-prefecture",
  "jp-local-151009": "niigata-city",
  "jp-local-261009": "kyoto-city",
  "jp-local-331007": "okayama-city",
  "jp-local-340006": "hiroshima-prefecture",
  "jp-local-341002": "hiroshima-city",
  "jp-local-260002": "kyoto-prefecture",
  "jp-local-330001": "okayama-prefecture",
  "jp-local-430005": "kumamoto-prefecture",
  "jp-local-070009": "fukushima-prefecture",
  "jp-local-221007": "shizuoka-city",
  "jp-local-221309": "hamamatsu-city",
  "jp-local-220001": "shizuoka-prefecture",
  "jp-local-040002": "miyagi-prefecture",
  "jp-local-281000": "kobe-city",
  "jp-local-041009": "sendai-city",
  "jp-local-280003": "hyogo-prefecture",
  "jp-local-121002": "chiba-city",
  "jp-local-120006": "chiba-prefecture",
  "jp-local-112038": "kawaguchi-city",
  "jp-local-110001": "saitama-prefecture",
  "jp-local-111007": "saitama-city",
  "jp-local-141305": "kawasaki-city",
  "jp-local-140007": "kanagawa-prefecture",
  "jp-local-141003": "yokohama-city",
  "jp-local-270008": "osaka-prefecture",
  "jp-local-271004": "osaka-city",
  "jp-local-271403": "sakai-city",
  "jp-local-010006": "hokkaido-prefecture",
  "jp-local-011002": "sapporo-city",
  "jp-local-012041": "asahikawa-city",
  "jp-local-230006": "aichi-prefecture",
  "jp-local-400009": "fukuoka-prefecture",
  "jp-local-401307": "fukuoka-city",
  "jp-local-401005": "kitakyushu-city",
  "jp-local-231002": "nagoya-city",
  "jp-local-232114": "toyota-city",
} as const;

const executiveSources = [
  ...sourceCatalog,
  ...(executiveCatalog.records as SourceRecord[]),
];

export const currentExecutiveTerms = executiveTerms as ExecutiveTerm[];
export const executiveEvidencePackets = evidencePackets as ExecutiveEvidencePacket[];
export const manifestoReviewRecords = manifestoReviews as ManifestoReview[];
export const manifestoReviewEvidencePackets =
  manifestoReviewPackets as ManifestoReviewEvidencePacket[];
export const manifestoSourceSearchRecords =
  manifestoSourceSearches as ManifestoSourceSearch[];
export const manifestoSourceSearchEvidencePackets =
  manifestoSourceSearchPackets as ManifestoSourceSearchEvidencePacket[];

export type PromiseRecord = {
  id: string;
  municipality_id: string;
  executive_term_id: string;
  original_text: string;
  source_location: string;
  statement_type:
    | "specific_commitment"
    | "directional_commitment"
    | "vision"
    | "supporting_context";
  plain_summary: string | null;
  policy_area: string;
  baseline: number | string | null;
  target: number | string | null;
  deadline: string | null;
  funding_statement: string | null;
  controllability: "high" | "medium" | "low" | "shared" | "not_assessable";
  assessability: "assessable" | "partially_assessable" | "not_assessable";
  progress_state:
    | "achieved"
    | "mostly_achieved"
    | "partially_achieved"
    | "in_progress"
    | "not_started"
    | "changed"
    | "abandoned"
    | "not_assessable";
  related_project_ids: string[];
  change_explanation: string | null;
  extraction_note: string | null;
  review_status: "verified" | "reviewed" | "extracted" | "inferred" | "missing";
  confidence: "high" | "medium" | "low" | "not_assessable";
  sources: string[];
};

export type PromiseEvidencePacket = {
  id: string;
  subject_type: "promise";
  subject_id: string;
  claims: EvidenceClaim[];
  open_questions: string[];
  review_status: "reviewed" | "verified";
};

export const promiseRecords = promises as PromiseRecord[];
export const promiseEvidencePackets =
  promisePackets as PromiseEvidencePacket[];

export function promisesForExecutive(term: ExecutiveTerm) {
  return promiseRecords.filter(
    (promise) => promise.executive_term_id === term.id,
  );
}

export function evidenceForPromise(promise: PromiseRecord) {
  return promiseEvidencePackets.find(
    (packet) => packet.subject_id === promise.id,
  );
}

export function executiveMunicipality(term: ExecutiveTerm) {
  const key = municipalityIdToKey[term.municipality_id as keyof typeof municipalityIdToKey];
  if (!key) {
    throw new Error(`Unknown executive municipality: ${term.municipality_id}`);
  }
  return { key, ...municipalityMeta[key] };
}

export function sourcesForExecutive(term: ExecutiveTerm) {
  return executiveSources.filter((source) => term.sources.includes(source.id));
}

export function manifestoSourcesForExecutive(term: ExecutiveTerm) {
  return executiveSources.filter((source) => term.manifesto_source_ids.includes(source.id));
}

export function evidenceForExecutive(term: ExecutiveTerm) {
  return executiveEvidencePackets.find((packet) => packet.subject_id === term.id);
}

export function manifestoReviewForExecutive(term: ExecutiveTerm) {
  return manifestoReviewRecords.find(
    (review) => review.executive_term_id === term.id,
  );
}

export function evidenceForManifestoReview(review: ManifestoReview) {
  return manifestoReviewEvidencePackets.find(
    (packet) => packet.subject_id === review.id,
  );
}

export function manifestoSourceSearchForExecutive(term: ExecutiveTerm) {
  return manifestoSourceSearchRecords.find(
    (search) => search.executive_term_id === term.id,
  );
}

export function evidenceForManifestoSourceSearch(search: ManifestoSourceSearch) {
  return manifestoSourceSearchEvidencePackets.find(
    (packet) => packet.subject_id === search.id,
  );
}

export function formatDateJa(value: string | null) {
  if (!value) {
    return "未確認";
  }
  return new Intl.DateTimeFormat("ja-JP", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "Asia/Tokyo",
  }).format(new Date(`${value}T00:00:00+09:00`));
}
