import evidencePackets from "../../../data/reviewed/kitakyushu-city/evidence_packets.json";
import fiscalRecords from "../../../data/reviewed/kitakyushu-city/fiscal_records.json";
import municipality from "../../../data/reviewed/kitakyushu-city/municipality.json";
import settlementEvidencePackets from "../../../data/reviewed/kitakyushu-city/settlement_evidence_packets.json";
import settlementRecords from "../../../data/reviewed/kitakyushu-city/settlement_records.json";

import type { EvidencePacket, FiscalRecord } from "./finance";

export const kitakyushuFinance = {
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

export function kitakyushuBudgetRecord(metric: string) {
  const record = kitakyushuFinance.records.find(
    (item) => item.metric === metric && item.stage === "initial_budget",
  );
  if (!record) {
    throw new Error(`Missing Kitakyushu budget record: ${metric}`);
  }
  return record;
}

export function kitakyushuSettlementRecord(metric: string) {
  const record = kitakyushuFinance.records.find(
    (item) => item.metric === metric && item.stage === "settlement",
  );
  if (!record) {
    throw new Error(`Missing Kitakyushu settlement record: ${metric}`);
  }
  return record;
}

export function evidenceForKitakyushuRecord(recordId: string) {
  return kitakyushuFinance.evidencePackets.find(
    (packet) => packet.subject_id === recordId,
  );
}
