import evidencePackets from "../../../data/reviewed/fukuoka-city/evidence_packets.json";
import fiscalRecords from "../../../data/reviewed/fukuoka-city/fiscal_records.json";
import municipality from "../../../data/reviewed/fukuoka-city/municipality.json";

import type { EvidencePacket, FiscalRecord } from "./finance";

export const fukuokaCityFinance = {
  municipality,
  records: fiscalRecords as FiscalRecord[],
  evidencePackets: evidencePackets as EvidencePacket[],
};

export function cityBudgetRecord(metric: string) {
  const record = fukuokaCityFinance.records.find(
    (item) => item.metric === metric && item.stage === "initial_budget",
  );
  if (!record) {
    throw new Error(`Missing reviewed Fukuoka City budget record: ${metric}`);
  }
  return record;
}

export function citySettlementRecord(metric: string) {
  const record = fukuokaCityFinance.records.find(
    (item) => item.metric === metric && item.stage === "settlement",
  );
  if (!record) {
    throw new Error(`Missing reviewed Fukuoka City settlement record: ${metric}`);
  }
  return record;
}

export function evidenceForCityRecord(recordId: string) {
  return fukuokaCityFinance.evidencePackets.find(
    (packet) => packet.subject_id === recordId,
  );
}
