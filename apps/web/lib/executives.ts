import executiveCatalog from "../../../data/catalog/executive_sources.json";
import evidencePackets from "../../../data/entities/executives/evidence_packets.json";
import executiveTerms from "../../../data/entities/executives/executive_terms.json";
import manifestoReviewPackets from "../../../data/entities/executives/manifesto_review_evidence_packets.json";
import manifestoReviews from "../../../data/entities/executives/manifesto_reviews.json";
import manifestoSourceSearchPackets from "../../../data/entities/executives/manifesto_source_search_evidence_packets.json";
import manifestoSourceSearches from "../../../data/entities/executives/manifesto_source_searches.json";

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
  "jp-local-400009": "fukuoka-prefecture",
  "jp-local-401307": "fukuoka-city",
  "jp-local-401005": "kitakyushu-city",
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
