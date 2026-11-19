import evidencePackets from "../../../data/reviewed/nagoya-city/evidence_packets.json";
import fiscalRecords from "../../../data/reviewed/nagoya-city/fiscal_records.json";
import municipality from "../../../data/reviewed/nagoya-city/municipality.json";

import type { EvidencePacket, FiscalRecord } from "./finance";

export const nagoyaCityFinance = {
  municipality,
  records: [...(fiscalRecords as FiscalRecord[])],
  evidencePackets: [...(evidencePackets as EvidencePacket[])],
};
