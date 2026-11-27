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
import iwatePrefectureMunicipality from "../../../data/reviewed/iwate-prefecture/municipality.json";
import iwatePrefecturePlan from "../../../data/reviewed/iwate-prefecture/plan_review.json";
import iwatePrefectureFiscal from "../../../data/reviewed/iwate-prefecture/fiscal_records.json";
import iwatePrefectureSettlement from "../../../data/reviewed/iwate-prefecture/settlement_records.json";
import iwatePrefectureBudgetEvidence from "../../../data/reviewed/iwate-prefecture/evidence_packets.json";
import iwatePrefectureSettlementEvidence from "../../../data/reviewed/iwate-prefecture/settlement_evidence_packets.json";
import iwatePrefectureSources from "../../../data/catalog/iwate_prefecture_finance_sources.json";
import moriokaCityMunicipality from "../../../data/reviewed/morioka-city/municipality.json";
import moriokaCityPlan from "../../../data/reviewed/morioka-city/plan_review.json";
import moriokaCityFiscal from "../../../data/reviewed/morioka-city/fiscal_records.json";
import moriokaCitySettlement from "../../../data/reviewed/morioka-city/settlement_records.json";
import moriokaCityBudgetEvidence from "../../../data/reviewed/morioka-city/evidence_packets.json";
import moriokaCitySettlementEvidence from "../../../data/reviewed/morioka-city/settlement_evidence_packets.json";
import moriokaCitySources from "../../../data/catalog/morioka_city_finance_sources.json";
import aomoriPrefectureMunicipality from "../../../data/reviewed/aomori-prefecture/municipality.json";
import aomoriPrefecturePlan from "../../../data/reviewed/aomori-prefecture/plan_review.json";
import aomoriPrefectureFiscal from "../../../data/reviewed/aomori-prefecture/fiscal_records.json";
import aomoriPrefectureSettlement from "../../../data/reviewed/aomori-prefecture/settlement_records.json";
import aomoriPrefectureBudgetEvidence from "../../../data/reviewed/aomori-prefecture/evidence_packets.json";
import aomoriPrefectureSettlementEvidence from "../../../data/reviewed/aomori-prefecture/settlement_evidence_packets.json";
import aomoriPrefectureSources from "../../../data/catalog/aomori_prefecture_finance_sources.json";
import aomoriCityMunicipality from "../../../data/reviewed/aomori-city/municipality.json";
import aomoriCityPlan from "../../../data/reviewed/aomori-city/plan_review.json";
import aomoriCityFiscal from "../../../data/reviewed/aomori-city/fiscal_records.json";
import aomoriCitySettlement from "../../../data/reviewed/aomori-city/settlement_records.json";
import aomoriCityBudgetEvidence from "../../../data/reviewed/aomori-city/evidence_packets.json";
import aomoriCitySettlementEvidence from "../../../data/reviewed/aomori-city/settlement_evidence_packets.json";
import aomoriCitySources from "../../../data/catalog/aomori_city_finance_sources.json";
export type TohokuSlug = "iwate-prefecture" | "morioka-city" | "aomori-prefecture" | "aomori-city" | "fukushima-prefecture" | "fukushima-city" | "yamagata-prefecture" | "yamagata-city" | "akita-prefecture" | "akita-city";
export type TohokuFinance = { municipality: {id:string; official_code:string;name_ja:string;last_verified_at:string;data_status:string}; records: FiscalRecord[]; evidencePackets: EvidencePacket[]; sources: SourceRecord[]; plan: {records: Array<{id:string;title:string;statement:string;decision:string;source_url?:string;evidence_location?:string}>; reviewed_at?:string; quality_boundary?:string} };
export const tohokuFinance: Record<TohokuSlug, TohokuFinance> = {
  "iwate-prefecture": {
    municipality: iwatePrefectureMunicipality,
    plan: iwatePrefecturePlan as TohokuFinance["plan"],
    records: [
      ...(iwatePrefectureFiscal as FiscalRecord[]),
      ...(iwatePrefectureSettlement as FiscalRecord[]),
    ],
    evidencePackets: [
      ...(iwatePrefectureBudgetEvidence as EvidencePacket[]),
      ...(iwatePrefectureSettlementEvidence as EvidencePacket[]),
    ],
    sources: iwatePrefectureSources.records as SourceRecord[],
  },
  "morioka-city": {
    municipality: moriokaCityMunicipality,
    plan: moriokaCityPlan as TohokuFinance["plan"],
    records: [
      ...(moriokaCityFiscal as FiscalRecord[]),
      ...(moriokaCitySettlement as FiscalRecord[]),
    ],
    evidencePackets: [
      ...(moriokaCityBudgetEvidence as EvidencePacket[]),
      ...(moriokaCitySettlementEvidence as EvidencePacket[]),
    ],
    sources: moriokaCitySources.records as SourceRecord[],
  },
  "aomori-prefecture": {
    municipality: aomoriPrefectureMunicipality,
    plan: aomoriPrefecturePlan as TohokuFinance["plan"],
    records: [
      ...(aomoriPrefectureFiscal as FiscalRecord[]),
      ...(aomoriPrefectureSettlement as FiscalRecord[]),
    ],
    evidencePackets: [
      ...(aomoriPrefectureBudgetEvidence as EvidencePacket[]),
      ...(aomoriPrefectureSettlementEvidence as EvidencePacket[]),
    ],
    sources: aomoriPrefectureSources.records as SourceRecord[],
  },
  "aomori-city": {
    municipality: aomoriCityMunicipality,
    plan: aomoriCityPlan as TohokuFinance["plan"],
    records: [
      ...(aomoriCityFiscal as FiscalRecord[]),
      ...(aomoriCitySettlement as FiscalRecord[]),
    ],
    evidencePackets: [
      ...(aomoriCityBudgetEvidence as EvidencePacket[]),
      ...(aomoriCitySettlementEvidence as EvidencePacket[]),
    ],
    sources: aomoriCitySources.records as SourceRecord[],
  },
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
