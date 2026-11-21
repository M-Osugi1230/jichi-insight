import municipality from "../../../data/reviewed/sendai-city/municipality.json";
import planReview from "../../../data/reviewed/sendai-city/plan_review.json";
import fiscalRecords from "../../../data/reviewed/sendai-city/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/sendai-city/settlement_records.json";
import evidencePackets from "../../../data/reviewed/sendai-city/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/sendai-city/settlement_evidence_packets.json";
import sourceCatalog from "../../../data/catalog/sendai_city_finance_sources.json";
import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

export const sendaiFinance = {
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

export const sendaiPlanReview = planReview;
export const sendaiFinanceSources = sourceCatalog.records as SourceRecord[];

export function sendaiBudgetRecord(metric: string): FiscalRecord | undefined {
  return sendaiFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}
export function sendaiEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return sendaiFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
