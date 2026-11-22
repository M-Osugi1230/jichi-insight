import municipality from "../../../data/reviewed/hiroshima-city/municipality.json";
import planReview from "../../../data/reviewed/hiroshima-city/plan_review.json";
import fiscalRecords from "../../../data/reviewed/hiroshima-city/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/hiroshima-city/settlement_records.json";
import evidencePackets from "../../../data/reviewed/hiroshima-city/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/hiroshima-city/settlement_evidence_packets.json";
import sources from "../../../data/catalog/hiroshima_city_finance_sources.json";
import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

export const hiroshimaCityFinance = {
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
export const hiroshimaCityPlanReview = planReview;
export const hiroshimaCityFinanceSources = sources.records as SourceRecord[];
export function hiroshimaCityBudgetRecord(metric: string): FiscalRecord | undefined {
  return hiroshimaCityFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}
export function hiroshimaCityEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return hiroshimaCityFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
