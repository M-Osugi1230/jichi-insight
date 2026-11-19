import municipality from "../../../data/reviewed/aichi-prefecture/municipality.json";
import planReview from "../../../data/reviewed/aichi-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/aichi-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/aichi-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/aichi-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/aichi-prefecture/settlement_evidence_packets.json";
import aichiSources from "../../../data/catalog/aichi_prefecture_finance_sources.json";

import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

export const aichiFinance = {
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

export const aichiPlanReview = planReview;
export const aichiFinanceSources = aichiSources.records as SourceRecord[];

export function aichiBudgetRecord(metric: string): FiscalRecord | undefined {
  return aichiFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function aichiEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return aichiFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
