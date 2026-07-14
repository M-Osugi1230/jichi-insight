import evidencePackets from "../../../data/reviewed/fukuoka-prefecture/evidence_packets.json";
import fiscalRecords from "../../../data/reviewed/fukuoka-prefecture/fiscal_records.json";
import municipality from "../../../data/reviewed/fukuoka-prefecture/municipality.json";
import settlementEvidencePackets from "../../../data/reviewed/fukuoka-prefecture/settlement_evidence_packets.json";
import settlementRecords from "../../../data/reviewed/fukuoka-prefecture/settlement_records.json";

import { sourceCatalog } from "./catalog";

export type FiscalRecord = {
  id: string;
  municipality_id: string;
  fiscal_year: number;
  account_type: "general" | "ordinary" | "special" | "public_enterprise" | "all_accounts";
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

export type SettlementYear = {
  fiscalYear: number;
  revenue: FiscalRecord;
  expenditure: FiscalRecord;
  formalBalanceYen: number | null;
};

export const fukuokaPrefectureFinance = {
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

export function fiscalRecordByMetric(metric: string) {
  const record = fukuokaPrefectureFinance.records.find(
    (item) => item.metric === metric && item.stage === "initial_budget",
  );
  if (!record) {
    throw new Error(`Missing reviewed fiscal record: ${metric}`);
  }
  return record;
}

export function settlementRecord(fiscalYear: number, metric: string) {
  const record = fukuokaPrefectureFinance.records.find(
    (item) =>
      item.fiscal_year === fiscalYear &&
      item.metric === metric &&
      item.stage === "settlement" &&
      item.account_type === "ordinary",
  );
  if (!record) {
    throw new Error(`Missing ordinary-account settlement: ${fiscalYear}/${metric}`);
  }
  return record;
}

export function settlementTrend(): SettlementYear[] {
  return [2020, 2021, 2022, 2023, 2024].map((fiscalYear) => {
    const revenue = settlementRecord(fiscalYear, "total_revenue");
    const expenditure = settlementRecord(fiscalYear, "total_expenditure");
    const formalBalanceYen =
      revenue.amount_yen !== null && expenditure.amount_yen !== null
        ? revenue.amount_yen - expenditure.amount_yen
        : null;
    return { fiscalYear, revenue, expenditure, formalBalanceYen };
  });
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

export function formatJapaneseYen(amount: number | null) {
  if (amount === null) {
    return "未確認";
  }
  const manYen = Math.trunc(amount / 10_000);
  const cho = Math.trunc(manYen / 100_000_000);
  const oku = Math.trunc((manYen % 100_000_000) / 10_000);
  const man = manYen % 10_000;
  const parts: string[] = [];
  if (cho > 0) {
    parts.push(`${cho}兆`);
  }
  if (oku > 0) {
    parts.push(`${new Intl.NumberFormat("ja-JP").format(oku)}億`);
  }
  if (man > 0) {
    parts.push(`${new Intl.NumberFormat("ja-JP").format(man)}万`);
  }
  return `${parts.join("")}円`;
}
