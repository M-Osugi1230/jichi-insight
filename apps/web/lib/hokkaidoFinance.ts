import municipality from "../../../data/reviewed/hokkaido-prefecture/municipality.json";
import planReview from "../../../data/reviewed/hokkaido-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/hokkaido-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/hokkaido-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/hokkaido-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/hokkaido-prefecture/settlement_evidence_packets.json";
import hokkaidoSources from "../../../data/catalog/hokkaido_prefecture_finance_sources.json";

import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

/** Reviewed fiscal sources only: initial general-account budget and ordinary-account settlement are distinct. */
export const hokkaidoFinance = {
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

export const hokkaidoPlanReview = planReview;
export const hokkaidoFinanceSources = hokkaidoSources.records as SourceRecord[];

export function hokkaidoBudgetRecord(metric: string): FiscalRecord | undefined {
  return hokkaidoFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function hokkaidoEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return hokkaidoFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
