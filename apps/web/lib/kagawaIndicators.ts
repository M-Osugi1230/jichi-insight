import evidencePart1 from "../../../data/evidence/kagawa_extended_plan_indicator_evidence_part1.json";
import evidencePart2 from "../../../data/evidence/kagawa_extended_plan_indicator_evidence_part2.json";
import evidencePart3 from "../../../data/evidence/kagawa_extended_plan_indicator_evidence_part3.json";
import manifest from "../../../data/catalog/kagawa_extended_plan_indicator_review_manifest.json";

type ClaimField = "indicator_name" | "current_value" | "target_r7" | "target_r8";

type EvidencePacket = {
  id: string;
  subject_id: string;
  source_url: string;
  source_pdf_page: number;
  source_table_row: number;
  claims: Array<{ field: ClaimField; value_original: string }>;
  review_status: "reviewed";
};

export type KagawaIndicator = {
  number: number;
  id: string;
  evidenceId: string;
  name: string;
  currentValue: string;
  targetR7: string;
  targetR8: string;
  sourceUrl: string;
  sourcePage: number;
  sourceRow: number;
  targetRevised: boolean;
  reposted: boolean;
};

function compactOriginal(value: string) {
  return value
    .replace(/(?<=[ぁ-んァ-ヶ一-龯々ー])\s+(?=[ぁ-んァ-ヶ一-龯々ー])/gu, "")
    .replace(/\s+/gu, " ")
    .trim();
}

function packetToIndicator(packet: EvidencePacket): KagawaIndicator {
  const claimByField = new Map(
    packet.claims.map((claim) => [claim.field, compactOriginal(claim.value_original)]),
  );
  const number = Number(packet.subject_id.slice(-3));
  const targetR7 = claimByField.get("target_r7") ?? "";
  const targetR8 = claimByField.get("target_r8") ?? "";
  return {
    number,
    id: packet.subject_id,
    evidenceId: packet.id,
    name: claimByField.get("indicator_name") ?? "",
    currentValue: claimByField.get("current_value") ?? "",
    targetR7,
    targetR8,
    sourceUrl: packet.source_url,
    sourcePage: packet.source_pdf_page,
    sourceRow: packet.source_table_row,
    targetRevised: targetR7 !== targetR8,
    reposted: manifest.reposted_indicator_numbers.includes(number),
  };
}

const packets = [
  ...evidencePart1.packets,
  ...evidencePart2.packets,
  ...evidencePart3.packets,
] as EvidencePacket[];

export const reviewedKagawaIndicators = packets.map(packetToIndicator);

export const kagawaIndicatorStats = {
  reviewedIndicators: manifest.reviewed_indicator_count,
  displayOccurrences: manifest.display_occurrence_count,
  evidencePackets: manifest.evidence_packet_count,
  repostedIndicators: manifest.reposted_indicator_count,
  targetRevisions: manifest.target_revision_count,
  currentValues: manifest.indicators_with_current_value_count,
  assessedIndicators: manifest.policy_achievement_assessed_indicator_count,
};

export const kagawaReviewManifest = manifest;
