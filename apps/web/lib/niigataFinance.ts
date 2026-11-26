import municipality from "../../../data/reviewed/niigata-prefecture/municipality.json";
import planReview from "../../../data/reviewed/niigata-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/niigata-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/niigata-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/niigata-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/niigata-prefecture/settlement_evidence_packets.json";
import sources from "../../../data/catalog/niigata_prefecture_finance_sources.json";
import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

import cityMunicipality from "../../../data/reviewed/niigata-city/municipality.json";
import cityPlanReview from "../../../data/reviewed/niigata-city/plan_review.json";
import cityFiscalRecords from "../../../data/reviewed/niigata-city/fiscal_records.json";
import citySettlementRecords from "../../../data/reviewed/niigata-city/settlement_records.json";
import cityEvidencePackets from "../../../data/reviewed/niigata-city/evidence_packets.json";
import citySettlementEvidencePackets from "../../../data/reviewed/niigata-city/settlement_evidence_packets.json";
import citySources from "../../../data/catalog/niigata_city_finance_sources.json";

export const niigataFinance = {
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
export const niigataPlanReview = planReview;
export const niigataFinanceSources = sources.records as SourceRecord[];

export function niigataBudgetRecord(metric: string): FiscalRecord | undefined {
  return niigataFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function niigataEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return niigataFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}


export const niigataCityFinance = {
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
export const niigataCityPlanReview = cityPlanReview;
export const niigataCityFinanceSources = citySources.records as SourceRecord[];

export function niigataCityBudgetRecord(metric: string): FiscalRecord | undefined {
  return niigataCityFinance.records.find((record) =>
    record.municipality_id === cityMunicipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function niigataCityEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return niigataCityFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
