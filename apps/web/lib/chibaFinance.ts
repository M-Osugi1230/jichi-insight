import municipality from "../../../data/reviewed/chiba-prefecture/municipality.json";
import planReview from "../../../data/reviewed/chiba-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/chiba-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/chiba-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/chiba-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/chiba-prefecture/settlement_evidence_packets.json";
import chibaSources from "../../../data/catalog/chiba_prefecture_finance_sources.json";

import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

/** Keep the enacted FY2026 general-account budget separate from FY2022–24 ordinary-account settlements. */
export const chibaFinance = {
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

export const chibaPlanReview = planReview;
export const chibaFinanceSources = chibaSources.records as SourceRecord[];

export function chibaBudgetRecord(metric: string): FiscalRecord | undefined {
  return chibaFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function chibaEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return chibaFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
