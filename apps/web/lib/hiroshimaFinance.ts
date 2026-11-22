import municipality from "../../../data/reviewed/hiroshima-prefecture/municipality.json";
import planReview from "../../../data/reviewed/hiroshima-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/hiroshima-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/hiroshima-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/hiroshima-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/hiroshima-prefecture/settlement_evidence_packets.json";
import sources from "../../../data/catalog/hiroshima_prefecture_finance_sources.json";
import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

export const hiroshimaFinance = {
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
export const hiroshimaPlanReview = planReview;
export const hiroshimaFinanceSources = sources.records as SourceRecord[];

export function hiroshimaBudgetRecord(metric: string): FiscalRecord | undefined {
  return hiroshimaFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function hiroshimaEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return hiroshimaFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
