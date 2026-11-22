import municipality from "../../../data/reviewed/kyoto-prefecture/municipality.json";
import planReview from "../../../data/reviewed/kyoto-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/kyoto-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/kyoto-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/kyoto-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/kyoto-prefecture/settlement_evidence_packets.json";
import sources from "../../../data/catalog/kyoto_prefecture_finance_sources.json";
import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

export const kyotoFinance = {
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
export const kyotoPlanReview = planReview;
export const kyotoFinanceSources = sources.records as SourceRecord[];

export function kyotoBudgetRecord(metric: string): FiscalRecord | undefined {
  return kyotoFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function kyotoEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return kyotoFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}

import cityMunicipality from "../../../data/reviewed/kyoto-city/municipality.json";
import cityPlanReview from "../../../data/reviewed/kyoto-city/plan_review.json";
import cityFiscalRecords from "../../../data/reviewed/kyoto-city/fiscal_records.json";
import citySettlementRecords from "../../../data/reviewed/kyoto-city/settlement_records.json";
import cityEvidencePackets from "../../../data/reviewed/kyoto-city/evidence_packets.json";
import citySettlementEvidencePackets from "../../../data/reviewed/kyoto-city/settlement_evidence_packets.json";
import citySources from "../../../data/catalog/kyoto_city_finance_sources.json";

export const kyotoCityFinance = {
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
export const kyotoCityPlanReview = cityPlanReview;
export const kyotoCityFinanceSources = citySources.records as SourceRecord[];

export function kyotoCityBudgetRecord(metric: string): FiscalRecord | undefined {
  return kyotoCityFinance.records.find((record) =>
    record.municipality_id === cityMunicipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function kyotoCityEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return kyotoCityFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
