import evidencePackets from "../../../data/reviewed/toyota-city/evidence_packets.json";
import fiscalRecords from "../../../data/reviewed/toyota-city/fiscal_records.json";
import municipality from "../../../data/reviewed/toyota-city/municipality.json";

import type { EvidencePacket, FiscalRecord } from "./finance";

export const toyotaCityFinance = {
  municipality,
  records: [...(fiscalRecords as FiscalRecord[])],
  evidencePackets: [...(evidencePackets as EvidencePacket[])],
};
