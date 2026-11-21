import municipality from "../../../data/reviewed/shizuoka-prefecture/municipality.json";
import planReview from "../../../data/reviewed/shizuoka-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/shizuoka-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/shizuoka-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/shizuoka-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/shizuoka-prefecture/settlement_evidence_packets.json";
import sources from "../../../data/catalog/shizuoka_prefecture_finance_sources.json";
import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

export const shizuokaFinance = {
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
export const shizuokaPlanReview = planReview;
export const shizuokaFinanceSources = sources.records as SourceRecord[];

export function shizuokaBudgetRecord(metric: string): FiscalRecord | undefined {
  return shizuokaFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}
export function shizuokaEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return shizuokaFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
