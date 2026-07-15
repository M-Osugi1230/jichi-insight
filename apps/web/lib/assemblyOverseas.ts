import evidencePackets from "../../../data/reviewed/fukuoka-prefecture/assembly/inspection_evidence_packets.json";
import trips from "../../../data/reviewed/fukuoka-prefecture/assembly/inspection_trips.json";

import { sourceCatalog } from "./catalog";
import type { EvidencePacket } from "./finance";

export type OverseasParticipant = {
  name: string;
  role: string;
  participant_type: "elected_member" | "coordinator" | "staff" | "other";
  funding_status: "public" | "personal" | "political_activity_expense" | "unknown";
};

export type InspectionTrip = {
  id: string;
  assembly_id: string;
  trip_type: "domestic" | "overseas";
  title: string;
  start_date: string;
  end_date: string;
  purpose: string;
  destinations: string[];
  participants: OverseasParticipant[];
  participant_count: number | null;
  total_cost_yen: number | null;
  cost_per_person_yen: number | null;
  cost_status: "available" | "not_published" | "not_found" | "not_applicable" | "unknown";
  report_status: "published" | "not_published" | "not_found" | "not_applicable" | "unknown";
  policy_follow_up: string[];
  review_status: string;
  confidence: string;
  sources: string[];
};

export const fukuokaOverseasActivities = trips as InspectionTrip[];
export const fukuokaOverseasEvidence = evidencePackets as EvidencePacket[];

export const overseasDisclosureSummary = {
  activities: fukuokaOverseasActivities.length,
  reportsPublished: fukuokaOverseasActivities.filter(
    (trip) => trip.report_status === "published",
  ).length,
  costsAvailable: fukuokaOverseasActivities.filter(
    (trip) => trip.cost_status === "available",
  ).length,
  participantListsAvailable: fukuokaOverseasActivities.filter(
    (trip) => trip.participant_count !== null,
  ).length,
};

export function evidenceForTrip(tripId: string) {
  return fukuokaOverseasEvidence.find((packet) => packet.subject_id === tripId);
}

export function sourcesForTrip(trip: InspectionTrip) {
  return sourceCatalog.filter((source) => trip.sources.includes(source.id));
}

export function formatActivityDate(start: string, end: string) {
  const startDate = new Date(`${start}T00:00:00+09:00`);
  const endDate = new Date(`${end}T00:00:00+09:00`);
  const formatter = new Intl.DateTimeFormat("ja-JP", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  return `${formatter.format(startDate)}〜${formatter.format(endDate)}`;
}
