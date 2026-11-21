import municipality from "../../../data/reviewed/hyogo-prefecture/municipality.json";
import planReview from "../../../data/reviewed/hyogo-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/hyogo-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/hyogo-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/hyogo-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/hyogo-prefecture/settlement_evidence_packets.json";
import hyogoSources from "../../../data/catalog/hyogo_prefecture_finance_sources.json";

import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

/** Keep the enacted FY2026 general-account budget separate from FY2022–24 ordinary-account settlements. */
export const hyogoFinance = {
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

export const hyogoPlanReview = planReview;
export const hyogoFinanceSources = hyogoSources.records as SourceRecord[];

export function hyogoBudgetRecord(metric: string): FiscalRecord | undefined {
  return hyogoFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function hyogoEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return hyogoFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
