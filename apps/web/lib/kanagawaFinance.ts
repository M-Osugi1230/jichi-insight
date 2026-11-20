import municipality from "../../../data/reviewed/kanagawa-prefecture/municipality.json";
import planReview from "../../../data/reviewed/kanagawa-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/kanagawa-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/kanagawa-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/kanagawa-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/kanagawa-prefecture/settlement_evidence_packets.json";
import kanagawaSources from "../../../data/catalog/kanagawa_prefecture_finance_sources.json";

import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

/** Keep the enacted general-account initial budget separate from ordinary-account settlements. */
export const kanagawaFinance = {
  municipality,
  records: [
    ...(fiscalRecords as FiscalRecord[]),
    ...(settlementRecords as FiscalRecord[]),
  ],
  evidencePackets: [
    ...(evidencePackets as EvidencePacket[]),
    ...(settlementEvidencePackets as EvidencePacket[]),
  ],
};

export const kanagawaPlanReview = planReview;
export const kanagawaFinanceSources = kanagawaSources.records as SourceRecord[];

export function kanagawaBudgetRecord(metric: string): FiscalRecord | undefined {
  return kanagawaFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function kanagawaEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return kanagawaFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
