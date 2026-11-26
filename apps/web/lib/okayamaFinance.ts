import municipality from "../../../data/reviewed/okayama-prefecture/municipality.json";
import planReview from "../../../data/reviewed/okayama-prefecture/plan_review.json";
import fiscalRecords from "../../../data/reviewed/okayama-prefecture/fiscal_records.json";
import settlementRecords from "../../../data/reviewed/okayama-prefecture/settlement_records.json";
import evidencePackets from "../../../data/reviewed/okayama-prefecture/evidence_packets.json";
import settlementEvidencePackets from "../../../data/reviewed/okayama-prefecture/settlement_evidence_packets.json";
import sources from "../../../data/catalog/okayama_prefecture_finance_sources.json";
import type { EvidencePacket, FiscalRecord } from "./finance";
import type { SourceRecord } from "./catalog";

import cityMunicipality from "../../../data/reviewed/okayama-city/municipality.json";
import cityPlanReview from "../../../data/reviewed/okayama-city/plan_review.json";
import cityFiscalRecords from "../../../data/reviewed/okayama-city/fiscal_records.json";
import citySettlementRecords from "../../../data/reviewed/okayama-city/settlement_records.json";
import cityEvidencePackets from "../../../data/reviewed/okayama-city/evidence_packets.json";
import citySettlementEvidencePackets from "../../../data/reviewed/okayama-city/settlement_evidence_packets.json";
import citySources from "../../../data/catalog/okayama_city_finance_sources.json";

export const okayamaFinance = {
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
export const okayamaPlanReview = planReview;
export const okayamaFinanceSources = sources.records as SourceRecord[];

export function okayamaBudgetRecord(metric: string): FiscalRecord | undefined {
  return okayamaFinance.records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function okayamaEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return okayamaFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}


export const okayamaCityFinance = {
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
export const okayamaCityPlanReview = cityPlanReview;
export const okayamaCityFinanceSources = citySources.records as SourceRecord[];

export function okayamaCityBudgetRecord(metric: string): FiscalRecord | undefined {
  return okayamaCityFinance.records.find((record) =>
    record.municipality_id === cityMunicipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}

export function okayamaCityEvidenceForRecord(recordId: string): EvidencePacket | undefined {
  return okayamaCityFinance.evidencePackets.find((packet) =>
    packet.subject_id === recordId &&
    (packet.review_status === "reviewed" || packet.review_status === "verified"),
  );
}
