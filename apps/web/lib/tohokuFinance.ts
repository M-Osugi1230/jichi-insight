import type { FiscalRecord, EvidencePacket } from "./finance";
import type { SourceRecord } from "./catalog";
import fukushimaPrefectureMunicipality from "../../../data/reviewed/fukushima-prefecture/municipality.json";
import fukushimaPrefecturePlan from "../../../data/reviewed/fukushima-prefecture/plan_review.json";
import fukushimaPrefectureFiscal from "../../../data/reviewed/fukushima-prefecture/fiscal_records.json";
import fukushimaPrefectureSettlement from "../../../data/reviewed/fukushima-prefecture/settlement_records.json";
import fukushimaPrefectureBudgetEvidence from "../../../data/reviewed/fukushima-prefecture/evidence_packets.json";
import fukushimaPrefectureSettlementEvidence from "../../../data/reviewed/fukushima-prefecture/settlement_evidence_packets.json";
import fukushimaPrefectureSources from "../../../data/catalog/fukushima_prefecture_finance_sources.json";
import fukushimaCityMunicipality from "../../../data/reviewed/fukushima-city/municipality.json";
import fukushimaCityPlan from "../../../data/reviewed/fukushima-city/plan_review.json";
import fukushimaCityFiscal from "../../../data/reviewed/fukushima-city/fiscal_records.json";
import fukushimaCitySettlement from "../../../data/reviewed/fukushima-city/settlement_records.json";
import fukushimaCityBudgetEvidence from "../../../data/reviewed/fukushima-city/evidence_packets.json";
import fukushimaCitySettlementEvidence from "../../../data/reviewed/fukushima-city/settlement_evidence_packets.json";
import fukushimaCitySources from "../../../data/catalog/fukushima_city_finance_sources.json";
import yamagataPrefectureMunicipality from "../../../data/reviewed/yamagata-prefecture/municipality.json";
import yamagataPrefecturePlan from "../../../data/reviewed/yamagata-prefecture/plan_review.json";
import yamagataPrefectureFiscal from "../../../data/reviewed/yamagata-prefecture/fiscal_records.json";
import yamagataPrefectureSettlement from "../../../data/reviewed/yamagata-prefecture/settlement_records.json";
import yamagataPrefectureBudgetEvidence from "../../../data/reviewed/yamagata-prefecture/evidence_packets.json";
import yamagataPrefectureSettlementEvidence from "../../../data/reviewed/yamagata-prefecture/settlement_evidence_packets.json";
import yamagataPrefectureSources from "../../../data/catalog/yamagata_prefecture_finance_sources.json";
import yamagataCityMunicipality from "../../../data/reviewed/yamagata-city/municipality.json";
import yamagataCityPlan from "../../../data/reviewed/yamagata-city/plan_review.json";
import yamagataCityFiscal from "../../../data/reviewed/yamagata-city/fiscal_records.json";
import yamagataCitySettlement from "../../../data/reviewed/yamagata-city/settlement_records.json";
import yamagataCityBudgetEvidence from "../../../data/reviewed/yamagata-city/evidence_packets.json";
import yamagataCitySettlementEvidence from "../../../data/reviewed/yamagata-city/settlement_evidence_packets.json";
import yamagataCitySources from "../../../data/catalog/yamagata_city_finance_sources.json";
import akitaPrefectureMunicipality from "../../../data/reviewed/akita-prefecture/municipality.json";
import akitaPrefecturePlan from "../../../data/reviewed/akita-prefecture/plan_review.json";
import akitaPrefectureFiscal from "../../../data/reviewed/akita-prefecture/fiscal_records.json";
import akitaPrefectureSettlement from "../../../data/reviewed/akita-prefecture/settlement_records.json";
import akitaPrefectureBudgetEvidence from "../../../data/reviewed/akita-prefecture/evidence_packets.json";
import akitaPrefectureSettlementEvidence from "../../../data/reviewed/akita-prefecture/settlement_evidence_packets.json";
import akitaPrefectureSources from "../../../data/catalog/akita_prefecture_finance_sources.json";
import akitaCityMunicipality from "../../../data/reviewed/akita-city/municipality.json";
import akitaCityPlan from "../../../data/reviewed/akita-city/plan_review.json";
import akitaCityFiscal from "../../../data/reviewed/akita-city/fiscal_records.json";
import akitaCitySettlement from "../../../data/reviewed/akita-city/settlement_records.json";
import akitaCityBudgetEvidence from "../../../data/reviewed/akita-city/evidence_packets.json";
import akitaCitySettlementEvidence from "../../../data/reviewed/akita-city/settlement_evidence_packets.json";
import akitaCitySources from "../../../data/catalog/akita_city_finance_sources.json";
export type TohokuSlug = "fukushima-prefecture" | "fukushima-city" | "yamagata-prefecture" | "yamagata-city" | "akita-prefecture" | "akita-city";
export type TohokuFinance = { municipality: {id:string; official_code:string;name_ja:string;last_verified_at:string;data_status:string}; records: FiscalRecord[]; evidencePackets: EvidencePacket[]; sources: SourceRecord[]; plan: {records: Array<{id:string;title:string;statement:string;decision:string;source_url?:string;evidence_location?:string}>; reviewed_at?:string; quality_boundary?:string} };
export const tohokuFinance: Record<TohokuSlug, TohokuFinance> = {
  "fukushima-prefecture": {
    municipality: fukushimaPrefectureMunicipality,
    plan: fukushimaPrefecturePlan as TohokuFinance["plan"],
    records: [...(fukushimaPrefectureFiscal as FiscalRecord[]), ...(fukushimaPrefectureSettlement as FiscalRecord[])],
    evidencePackets: [...(fukushimaPrefectureBudgetEvidence as EvidencePacket[]), ...(fukushimaPrefectureSettlementEvidence as EvidencePacket[])],
    sources: fukushimaPrefectureSources.records as SourceRecord[],
  },
  "fukushima-city": {
    municipality: fukushimaCityMunicipality,
    plan: fukushimaCityPlan as TohokuFinance["plan"],
    records: [...(fukushimaCityFiscal as FiscalRecord[]), ...(fukushimaCitySettlement as FiscalRecord[])],
    evidencePackets: [...(fukushimaCityBudgetEvidence as EvidencePacket[]), ...(fukushimaCitySettlementEvidence as EvidencePacket[])],
    sources: fukushimaCitySources.records as SourceRecord[],
  },
  "yamagata-prefecture": {
    municipality: yamagataPrefectureMunicipality,
    plan: yamagataPrefecturePlan as TohokuFinance["plan"],
    records: [...(yamagataPrefectureFiscal as FiscalRecord[]), ...(yamagataPrefectureSettlement as FiscalRecord[])],
    evidencePackets: [...(yamagataPrefectureBudgetEvidence as EvidencePacket[]), ...(yamagataPrefectureSettlementEvidence as EvidencePacket[])],
    sources: yamagataPrefectureSources.records as SourceRecord[],
  },
  "yamagata-city": {
    municipality: yamagataCityMunicipality,
    plan: yamagataCityPlan as TohokuFinance["plan"],
    records: [...(yamagataCityFiscal as FiscalRecord[]), ...(yamagataCitySettlement as FiscalRecord[])],
    evidencePackets: [...(yamagataCityBudgetEvidence as EvidencePacket[]), ...(yamagataCitySettlementEvidence as EvidencePacket[])],
    sources: yamagataCitySources.records as SourceRecord[],
  },
  "akita-prefecture": {
    municipality: akitaPrefectureMunicipality,
    plan: akitaPrefecturePlan as TohokuFinance["plan"],
    records: [...(akitaPrefectureFiscal as FiscalRecord[]), ...(akitaPrefectureSettlement as FiscalRecord[])],
    evidencePackets: [...(akitaPrefectureBudgetEvidence as EvidencePacket[]), ...(akitaPrefectureSettlementEvidence as EvidencePacket[])],
    sources: akitaPrefectureSources.records as SourceRecord[],
  },
  "akita-city": {
    municipality: akitaCityMunicipality,
    plan: akitaCityPlan as TohokuFinance["plan"],
    records: [...(akitaCityFiscal as FiscalRecord[]), ...(akitaCitySettlement as FiscalRecord[])],
    evidencePackets: [...(akitaCityBudgetEvidence as EvidencePacket[]), ...(akitaCitySettlementEvidence as EvidencePacket[])],
    sources: akitaCitySources.records as SourceRecord[],
  },
};
export function tohokuBudgetRecord(slug: TohokuSlug, metric: string) {
  const { records, municipality } = tohokuFinance[slug];
  return records.find((record) =>
    record.municipality_id === municipality.id &&
    record.review_status === "reviewed" &&
    record.stage === "initial_budget" &&
    record.account_type === "general" &&
    record.fiscal_year === 2026 &&
    record.metric === metric,
  );
}
