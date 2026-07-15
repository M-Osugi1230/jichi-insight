import evidencePackets from "../../../data/entities/executives/source_request_evidence_packets.json";
import sourceRequests from "../../../data/entities/executives/source_requests.json";

import {
  currentExecutiveTerms,
  executiveMunicipality,
  type EvidenceClaim,
  type ExecutiveTerm,
} from "./executives";

export type SourceRequestChannel = {
  kind: "email" | "phone" | "fax" | "contact_page";
  value: string;
  public_source_id: string;
};

export type SourceRequest = {
  id: string;
  executive_term_id: string;
  manifesto_source_search_id: string;
  organization: string;
  contact_channels: SourceRequestChannel[];
  subject: string;
  request_body: string;
  requested_items: string[];
  status: "draft" | "ready_for_review" | "sent" | "answered" | "no_record" | "closed";
  prepared_at: string;
  sent_at: string | null;
  response_received_at: string | null;
  response_summary: string | null;
  privacy_note: string | null;
  source_ids: string[];
  review_status: "reviewed" | "verified";
  confidence: "high" | "medium" | "low" | "not_assessable";
};

export type SourceRequestEvidencePacket = {
  id: string;
  subject_type: "source_request";
  subject_id: string;
  claims: EvidenceClaim[];
  open_questions: string[];
  review_status: "reviewed" | "verified";
};

export const sourceRequestRecords = sourceRequests as SourceRequest[];
export const sourceRequestEvidencePackets = evidencePackets as SourceRequestEvidencePacket[];

export function executiveForSourceRequest(request: SourceRequest): ExecutiveTerm {
  const term = currentExecutiveTerms.find((item) => item.id === request.executive_term_id);
  if (!term) {
    throw new Error(`Unknown executive term for source request: ${request.id}`);
  }
  return term;
}

export function municipalityForSourceRequest(request: SourceRequest) {
  return executiveMunicipality(executiveForSourceRequest(request));
}

export function evidenceForSourceRequest(request: SourceRequest) {
  return sourceRequestEvidencePackets.find((packet) => packet.subject_id === request.id);
}

export function sourceRequestStatusLabel(status: SourceRequest["status"]) {
  const labels: Record<SourceRequest["status"], string> = {
    draft: "照会案・未送信",
    ready_for_review: "送信前レビュー中",
    sent: "送信済み",
    answered: "回答受領",
    no_record: "保有記録なしの回答",
    closed: "対応終了",
  };
  return labels[status];
}

export function sourceRequestChannelLabel(kind: SourceRequestChannel["kind"]) {
  const labels: Record<SourceRequestChannel["kind"], string> = {
    email: "メール",
    phone: "電話",
    fax: "FAX",
    contact_page: "問い合わせページ",
  };
  return labels[kind];
}
