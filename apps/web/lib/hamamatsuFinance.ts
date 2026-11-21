import municipality from "../../../data/reviewed/hamamatsu-city/municipality.json";
import planReview from "../../../data/reviewed/hamamatsu-city/plan_review.json";
import fiscalRecords from "../../../data/reviewed/hamamatsu-city/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/hamamatsu-city/settlement_records.json";
import evidencePackets from "../../../data/reviewed/hamamatsu-city/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/hamamatsu-city/settlement_evidence_packets.json";
import sources from "../../../data/catalog/hamamatsu_city_finance_sources.json";
import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

export const hamamatsuFinance = {
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
export const hamamatsuPlanReview = planReview;
export const hamamatsuFinanceSources = sources.records as SourceRecord[];

export function hamamatsuBudgetRecord(metric: string): FiscalRecord | undefined {
  return hamamatsuFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}
export function hamamatsuEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return hamamatsuFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
