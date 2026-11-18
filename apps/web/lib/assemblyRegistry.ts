import prefAssembly from "../../../data/reviewed/fukuoka-prefecture/assembly/assembly_records.json";
import prefDisclosure from "../../../data/reviewed/fukuoka-prefecture/assembly/disclosure_profiles.json";
import prefSessions from "../../../data/reviewed/fukuoka-prefecture/assembly/sessions.json";
import prefProposals from "../../../data/reviewed/fukuoka-prefecture/assembly/proposals.json";
import prefVotes from "../../../data/reviewed/fukuoka-prefecture/assembly/votes.json";
import prefFactionVotes from "../../../data/reviewed/fukuoka-prefecture/assembly/faction_votes.json";
import prefExpenses from "../../../data/reviewed/fukuoka-prefecture/assembly/political_activity_expenses.json";
import prefTrips from "../../../data/reviewed/fukuoka-prefecture/assembly/inspection_trips.json";
import prefAssemblyEvidence from "../../../data/reviewed/fukuoka-prefecture/assembly/assembly_evidence_packets.json";
import prefVoteEvidence from "../../../data/reviewed/fukuoka-prefecture/assembly/proposal_vote_evidence_packets.json";
import prefExpenseEvidence from "../../../data/reviewed/fukuoka-prefecture/assembly/expense_evidence_packets.json";
import prefTripEvidence from "../../../data/reviewed/fukuoka-prefecture/assembly/inspection_evidence_packets.json";
import cityAssembly from "../../../data/reviewed/fukuoka-city/assembly/assembly_records.json";
import cityDisclosure from "../../../data/reviewed/fukuoka-city/assembly/disclosure_profiles.json";
import citySessions from "../../../data/reviewed/fukuoka-city/assembly/sessions.json";
import cityProposals from "../../../data/reviewed/fukuoka-city/assembly/proposals.json";
import cityVotes from "../../../data/reviewed/fukuoka-city/assembly/votes.json";
import cityFactionVotes from "../../../data/reviewed/fukuoka-city/assembly/faction_votes.json";
import cityExpenses from "../../../data/reviewed/fukuoka-city/assembly/political_activity_expenses.json";
import cityTrips from "../../../data/reviewed/fukuoka-city/assembly/inspection_trips.json";
import cityAssemblyEvidence from "../../../data/reviewed/fukuoka-city/assembly/assembly_evidence_packets.json";
import cityVoteEvidence from "../../../data/reviewed/fukuoka-city/assembly/proposal_vote_evidence_packets.json";
import cityExpenseEvidence from "../../../data/reviewed/fukuoka-city/assembly/expense_evidence_packets.json";
import cityTripEvidence from "../../../data/reviewed/fukuoka-city/assembly/inspection_evidence_packets.json";
import kitaAssembly from "../../../data/reviewed/kitakyushu-city/assembly/assembly_records.json";
import kitaDisclosure from "../../../data/reviewed/kitakyushu-city/assembly/disclosure_profiles.json";
import kitaSessions from "../../../data/reviewed/kitakyushu-city/assembly/sessions.json";
import kitaProposals from "../../../data/reviewed/kitakyushu-city/assembly/proposals.json";
import kitaVotes from "../../../data/reviewed/kitakyushu-city/assembly/votes.json";
import kitaFactionVotes from "../../../data/reviewed/kitakyushu-city/assembly/faction_votes.json";
import kitaExpenses from "../../../data/reviewed/kitakyushu-city/assembly/political_activity_expenses.json";
import kitaAssemblyEvidence from "../../../data/reviewed/kitakyushu-city/assembly/assembly_evidence_packets.json";
import kitaVoteEvidence from "../../../data/reviewed/kitakyushu-city/assembly/proposal_vote_evidence_packets.json";
import kitaExpenseEvidence from "../../../data/reviewed/kitakyushu-city/assembly/expense_evidence_packets.json";
import prefSources from "../../../data/catalog/fukuoka_assembly_sources.json";
import citySources from "../../../data/catalog/fukuoka_city_assembly_sources.json";
import kitaSources from "../../../data/catalog/kitakyushu_assembly_sources.json";

export type AssemblySlug = "fukuoka-prefecture" | "fukuoka-city" | "kitakyushu-city";
export type Assembly = {
  id: string; name: string; seat_count: number;
  term_start: string; term_end: string;
  factions: { name: string; member_count: number }[];
  committees: string[]; sources: string[]; review_status: string;
};
export type DisclosureItem = {
  item: string; availability: string; granularity: string;
  note: string; source_url: string | null;
};
export type Disclosure = {
  items: DisclosureItem[]; as_of: string; sources: string[]; review_status: string;
};
export type Session = {
  id: string; name: string; start_date: string | null;
  end_date: string | null; sources: string[];
};
export type Proposal = {
  id: string; session_id: string; proposal_number: string; title: string;
  submitted_by: string; decided_at: string | null; submitted_at: string | null;
  outcome: string; related_fiscal_record_ids: string[]; sources: string[];
};
export type Vote = {
  id: string; proposal_id: string; member_vote_availability: string;
  totals: { for?: number; against?: number } | null;
  vote_date: string | null; sources: string[];
};
export type FactionVote = {
  id: string; vote_id: string; faction_name: string; member_count: number | null;
  position: string; sources: string[];
};
export type Expense = {
  id: string; fiscal_year: number; recipient_name: string; recipient_type: string;
  granted_yen: number | null; spent_yen: number | null; returned_yen: number | null;
  breakdown: { category: string; amount_yen: number | null }[];
  receipt_access: string; report_status: string; sources: string[];
};
export type Trip = {
  id: string; title: string; start_date: string | null; end_date: string | null;
  purpose: string | null; destinations: string[]; participants: {
    name: string; role: string; participant_type: string;
  }[];
  participant_count: number | null; total_cost_yen: number | null;
  cost_status: string; report_status: string; policy_follow_up: string[];
  sources: string[];
};
export type Evidence = {
  subject_id: string; review_status: string; open_questions: string[];
  claims: { field: string; statement: string; source_ids: string[]; location_note: string | null; decision: string }[];
};
export type AssemblySource = {
  id: string; title: string; url: string; indexed_at: string;
  review_status: string; notes: string;
};
type Registry = {
  assembly: Assembly; disclosure: Disclosure; sessions: Session[];
  proposals: Proposal[]; votes: Vote[]; factionVotes: FactionVote[];
  expenses: Expense[]; trips: Trip[]; evidence: Evidence[];
  sources: AssemblySource[];
};
function registry(
  assemblies: Assembly[], profiles: Disclosure[], sessions: Session[],
  proposals: Proposal[], votes: Vote[], factionVotes: FactionVote[],
  expenses: Expense[], trips: Trip[], evidence: Evidence[], sources: AssemblySource[],
): Registry {
  if (assemblies.length !== 1 || profiles.length !== 1) {
    throw new Error("Expected one Reviewed assembly and disclosure profile");
  }
  return {
    assembly: assemblies[0], disclosure: profiles[0], sessions, proposals, votes,
    factionVotes, expenses, trips, evidence, sources,
  };
}
export const assemblies: Record<AssemblySlug, Registry> = {
  "fukuoka-prefecture": registry(
    prefAssembly, prefDisclosure, prefSessions, prefProposals, prefVotes,
    prefFactionVotes, prefExpenses, prefTrips,
    [...prefAssemblyEvidence, ...prefVoteEvidence, ...prefExpenseEvidence, ...prefTripEvidence],
    prefSources.records,
  ),
  "fukuoka-city": registry(
    cityAssembly, cityDisclosure, citySessions, cityProposals, cityVotes,
    cityFactionVotes, cityExpenses, cityTrips,
    [...cityAssemblyEvidence, ...cityVoteEvidence, ...cityExpenseEvidence, ...cityTripEvidence],
    citySources.records,
  ),
  "kitakyushu-city": registry(
    kitaAssembly, kitaDisclosure, kitaSessions, kitaProposals, kitaVotes,
    kitaFactionVotes, kitaExpenses, [],
    [...kitaAssemblyEvidence, ...kitaVoteEvidence, ...kitaExpenseEvidence],
    kitaSources.records,
  ),
};
export const assemblySlugs: AssemblySlug[] = [
  "fukuoka-prefecture", "fukuoka-city", "kitakyushu-city",
];
export function isAssemblySlug(slug: string): slug is AssemblySlug {
  return Object.prototype.hasOwnProperty.call(assemblies, slug);
}
export function evidenceFor(registry: Registry, id: string): Evidence[] {
  return registry.evidence.filter((packet) => packet.subject_id === id);
}
