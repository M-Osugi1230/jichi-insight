import municipality from "../../../data/reviewed/saitama-prefecture/municipality.json";
import planReview from "../../../data/reviewed/saitama-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/saitama-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/saitama-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/saitama-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/saitama-prefecture/settlement_evidence_packets.json";
import saitamaSources from "../../../data/catalog/saitama_prefecture_finance_sources.json";

import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

/** General-account FY2026 enacted budget and FY2022–24 ordinary-account settlements stay distinct. */
export const saitamaFinance = {
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
export const saitamaPlanReview = planReview;
export const saitamaFinanceSources = saitamaSources.records as SourceRecord[];

export function saitamaBudgetRecord(metric: string): FiscalRecord | undefined {
  return saitamaFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function saitamaEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return saitamaFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
