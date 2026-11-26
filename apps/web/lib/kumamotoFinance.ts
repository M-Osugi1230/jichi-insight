import municipality from "../../../data/reviewed/kumamoto-prefecture/municipality.json";
import planReview from "../../../data/reviewed/kumamoto-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/kumamoto-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/kumamoto-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/kumamoto-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/kumamoto-prefecture/settlement_evidence_packets.json";
import sources from "../../../data/catalog/kumamoto_prefecture_finance_sources.json";
import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

import cityMunicipality from "../../../data/reviewed/kumamoto-city/municipality.json";
import cityPlanReview from "../../../data/reviewed/kumamoto-city/plan_review.json";
import cityFiscalRecords from "../../../data/reviewed/kumamoto-city/fiscal_records.json";
import citySettlementRecords from "../../../data/reviewed/kumamoto-city/settlement_records.json";
import cityEvidencePackets from "../../../data/reviewed/kumamoto-city/evidence_packets.json";
import citySettlementEvidencePackets from "../../../data/reviewed/kumamoto-city/settlement_evidence_packets.json";
import citySources from "../../../data/catalog/kumamoto_city_finance_sources.json";

export const kumamotoFinance = {
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
export const kumamotoPlanReview = planReview;
export const kumamotoFinanceSources = sources.records as SourceRecord[];

export function kumamotoBudgetRecord(metric: string): FiscalRecord | undefined {
  return kumamotoFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function kumamotoEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return kumamotoFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}


export const kumamotoCityFinance = {
  municipality: cityMunicipality,
  records: [
    ...(cityFiscalRecords as FiscalRecord[]),
    ...(citySettlementRecords as FiscalRecord[]),
  ],
  evidencePackets: [
    ...(cityEvidencePackets as EvidencePacket[]),
    ...(citySettlementEvidencePackets as EvidencePacket[]),
  ],
};
export const kumamotoCityPlanReview = cityPlanReview;
export const kumamotoCityFinanceSources = citySources.records as SourceRecord[];

export function kumamotoCityBudgetRecord(metric: string): FiscalRecord | undefined {
  return kumamotoCityFinance.records.find((record) =>
    record.municipality_id === cityMunicipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function kumamotoCityEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return kumamotoCityFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
