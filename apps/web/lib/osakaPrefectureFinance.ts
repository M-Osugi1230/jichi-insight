import municipality from "../../../data/reviewed/osaka-prefecture/municipality.json";
import planReview from "../../../data/reviewed/osaka-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/osaka-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/osaka-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/osaka-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/osaka-prefecture/settlement_evidence_packets.json";
import osakaSources from "../../../data/catalog/osaka_prefecture_finance_sources.json";

import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

/** Reviewed fiscal sources only: initial general-account budget and ordinary-account settlement are distinct. */
export const osakaFinance = {
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

export const osakaPlanReview = planReview;
export const osakaFinanceSources = osakaSources.records as SourceRecord[];

export function osakaBudgetRecord(metric: string): FiscalRecord | undefined {
  return osakaFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function osakaEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return osakaFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
