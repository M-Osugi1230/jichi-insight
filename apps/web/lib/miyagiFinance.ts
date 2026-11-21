import municipality from "../../../data/reviewed/miyagi-prefecture/municipality.json";
import planReview from "../../../data/reviewed/miyagi-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/miyagi-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/miyagi-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/miyagi-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/miyagi-prefecture/settlement_evidence_packets.json";
import sourceCatalog from "../../../data/catalog/miyagi_prefecture_finance_sources.json";
import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

export const miyagiFinance = {
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

export const miyagiPlanReview = planReview;
export const miyagiFinanceSources = sourceCatalog.records as SourceRecord[];

export function miyagiBudgetRecord(metric: string): FiscalRecord | undefined {
  return miyagiFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}
export function miyagiEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return miyagiFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
