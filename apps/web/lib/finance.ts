import evidencePackets from "../../../data/reviewed/fukuoka-prefecture/evidence_packets.json";
import fiscalRecords from "../../../data/reviewed/fukuoka-prefecture/fiscal_records.json";
import municipality from "../../../data/reviewed/fukuoka-prefecture/municipality.json";

import { sourceCatalog } from "./catalog";

export type FiscalRecord = {
  id: string;
  municipality_id: string;
  fiscal_year: number;
  account_type: "general" | "special" | "public_enterprise" | "all_accounts";
  stage: "initial_budget" | "revised_budget" | "execution" | "settlement";
  metric: string;
  metric_label: string | null;
  amount_yen: number | null;
  value: number | null;
  unit: string;
  value_status: string;
  period_start: string | null;
  period_end: string | null;
  note: string | null;
  review_status: string;
  confidence: string;
  sources: string[];
};

export type EvidencePacket = {
  id: string;
  subject_type: string;
  subject_id: string;
  claims: Array<{
    field: string;
    statement: string;
    source_ids: string[];
    location_note: string | null;
    decision: string;
    review_note: string | null;
  }>;
  open_questions: string[];
  review_status: string;
};

export const fukuokaPrefectureFinance = {
  municipality,
  records: fiscalRecords as FiscalRecord[],
  evidencePackets: evidencePackets as EvidencePacket[],
};

export function fiscalRecordByMetric(metric: string) {
  const record = fukuokaPrefectureFinance.records.find((item) => item.metric === metric);
  if (!record) {
    throw new Error(`Missing reviewed fiscal record: ${metric}`);
  }
  return record;
}

export function evidenceForRecord(recordId: string) {
  return fukuokaPrefectureFinance.evidencePackets.find(
    (packet) => packet.subject_id === recordId,
  );
}

export function sourcesForRecord(record: FiscalRecord) {
  return sourceCatalog.filter((source) => record.sources.includes(source.id));
}

export function formatExactYen(amount: number | null) {
  if (amount === null) {
    return "未確認";
  }
  return `${new Intl.NumberFormat("ja-JP").format(amount)}円`;
}

export function formatCompactYen(amount: number | null) {
  if (amount === null) {
    return "未確認";
  }
  if (amount >= 1_000_000_000_000) {
    const value = amount / 1_000_000_000_000;
    return `${Number.isInteger(value) ? value.toFixed(0) : value.toFixed(1)}兆円`;
  }
  if (amount >= 100_000_000) {
    return `${new Intl.NumberFormat("ja-JP", { maximumFractionDigits: 0 }).format(
      amount / 100_000_000,
    )}億円`;
  }
  return formatExactYen(amount);
}
