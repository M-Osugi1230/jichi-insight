// Saitama cluster: reviewed assembly records and source disclosure profiles.
import saitamaPrefAssembly from "../../../data/reviewed/saitama-prefecture/assembly/assembly_records.json";
import saitamaPrefDisclosure from "../../../data/reviewed/saitama-prefecture/assembly/disclosure_profiles.json";
import saitamaPrefSessions from "../../../data/reviewed/saitama-prefecture/assembly/sessions.json";
import saitamaPrefProposals from "../../../data/reviewed/saitama-prefecture/assembly/proposals.json";
import saitamaPrefVotes from "../../../data/reviewed/saitama-prefecture/assembly/votes.json";
import saitamaPrefFactionVotes from "../../../data/reviewed/saitama-prefecture/assembly/faction_votes.json";
import saitamaPrefExpenses from "../../../data/reviewed/saitama-prefecture/assembly/political_activity_expenses.json";
import saitamaPrefTrips from "../../../data/reviewed/saitama-prefecture/assembly/inspection_trips.json";
import saitamaPrefAssemblyEvidence from "../../../data/reviewed/saitama-prefecture/assembly/assembly_evidence_packets.json";
import saitamaPrefVoteEvidence from "../../../data/reviewed/saitama-prefecture/assembly/proposal_vote_evidence_packets.json";
import saitamaPrefExpenseEvidence from "../../../data/reviewed/saitama-prefecture/assembly/expense_evidence_packets.json";
import saitamaPrefTripEvidence from "../../../data/reviewed/saitama-prefecture/assembly/inspection_evidence_packets.json";
import saitamaPrefSources from "../../../data/catalog/saitama_prefecture_assembly_sources.json";
import saitamaCityAssembly from "../../../data/reviewed/saitama-city/assembly/assembly_records.json";
import saitamaCityDisclosure from "../../../data/reviewed/saitama-city/assembly/disclosure_profiles.json";
import saitamaCitySessions from "../../../data/reviewed/saitama-city/assembly/sessions.json";
import saitamaCityProposals from "../../../data/reviewed/saitama-city/assembly/proposals.json";
import saitamaCityVotes from "../../../data/reviewed/saitama-city/assembly/votes.json";
import saitamaCityFactionVotes from "../../../data/reviewed/saitama-city/assembly/faction_votes.json";
import saitamaCityExpenses from "../../../data/reviewed/saitama-city/assembly/political_activity_expenses.json";
import saitamaCityTrips from "../../../data/reviewed/saitama-city/assembly/inspection_trips.json";
import saitamaCityAssemblyEvidence from "../../../data/reviewed/saitama-city/assembly/assembly_evidence_packets.json";
import saitamaCityVoteEvidence from "../../../data/reviewed/saitama-city/assembly/proposal_vote_evidence_packets.json";
import saitamaCityExpenseEvidence from "../../../data/reviewed/saitama-city/assembly/expense_evidence_packets.json";
import saitamaCityTripEvidence from "../../../data/reviewed/saitama-city/assembly/inspection_evidence_packets.json";
import saitamaCitySources from "../../../data/catalog/saitama_city_assembly_sources.json";
import kawaguchiAssembly from "../../../data/reviewed/kawaguchi-city/assembly/assembly_records.json";
import kawaguchiDisclosure from "../../../data/reviewed/kawaguchi-city/assembly/disclosure_profiles.json";
import kawaguchiSessions from "../../../data/reviewed/kawaguchi-city/assembly/sessions.json";
import kawaguchiProposals from "../../../data/reviewed/kawaguchi-city/assembly/proposals.json";
import kawaguchiVotes from "../../../data/reviewed/kawaguchi-city/assembly/votes.json";
import kawaguchiFactionVotes from "../../../data/reviewed/kawaguchi-city/assembly/faction_votes.json";
import kawaguchiExpenses from "../../../data/reviewed/kawaguchi-city/assembly/political_activity_expenses.json";
import kawaguchiTrips from "../../../data/reviewed/kawaguchi-city/assembly/inspection_trips.json";
import kawaguchiAssemblyEvidence from "../../../data/reviewed/kawaguchi-city/assembly/assembly_evidence_packets.json";
import kawaguchiVoteEvidence from "../../../data/reviewed/kawaguchi-city/assembly/proposal_vote_evidence_packets.json";
import kawaguchiExpenseEvidence from "../../../data/reviewed/kawaguchi-city/assembly/expense_evidence_packets.json";
import kawaguchiTripEvidence from "../../../data/reviewed/kawaguchi-city/assembly/inspection_evidence_packets.json";
import kawaguchiSources from "../../../data/catalog/kawaguchi_city_assembly_sources.json";
import osakaPrefAssembly from "../../../data/reviewed/osaka-prefecture/assembly/assembly_records.json";
import osakaPrefDisclosure from "../../../data/reviewed/osaka-prefecture/assembly/disclosure_profiles.json";
import osakaPrefSessions from "../../../data/reviewed/osaka-prefecture/assembly/sessions.json";
import osakaPrefProposals from "../../../data/reviewed/osaka-prefecture/assembly/proposals.json";
import osakaPrefVotes from "../../../data/reviewed/osaka-prefecture/assembly/votes.json";
import osakaPrefFactionVotes from "../../../data/reviewed/osaka-prefecture/assembly/faction_votes.json";
import osakaPrefExpenses from "../../../data/reviewed/osaka-prefecture/assembly/political_activity_expenses.json";
import osakaPrefTrips from "../../../data/reviewed/osaka-prefecture/assembly/inspection_trips.json";
import osakaPrefAssemblyEvidence from "../../../data/reviewed/osaka-prefecture/assembly/assembly_evidence_packets.json";
import osakaPrefVoteEvidence from "../../../data/reviewed/osaka-prefecture/assembly/proposal_vote_evidence_packets.json";
import osakaPrefExpenseEvidence from "../../../data/reviewed/osaka-prefecture/assembly/expense_evidence_packets.json";
import osakaPrefTripEvidence from "../../../data/reviewed/osaka-prefecture/assembly/inspection_evidence_packets.json";
import osakaPrefSources from "../../../data/catalog/osaka_prefecture_assembly_sources.json";
import osakaCityAssembly from "../../../data/reviewed/osaka-city/assembly/assembly_records.json";
import osakaCityDisclosure from "../../../data/reviewed/osaka-city/assembly/disclosure_profiles.json";
import osakaCitySessions from "../../../data/reviewed/osaka-city/assembly/sessions.json";
import osakaCityProposals from "../../../data/reviewed/osaka-city/assembly/proposals.json";
import osakaCityVotes from "../../../data/reviewed/osaka-city/assembly/votes.json";
import osakaCityFactionVotes from "../../../data/reviewed/osaka-city/assembly/faction_votes.json";
import osakaCityExpenses from "../../../data/reviewed/osaka-city/assembly/political_activity_expenses.json";
import osakaCityTrips from "../../../data/reviewed/osaka-city/assembly/inspection_trips.json";
import osakaCityAssemblyEvidence from "../../../data/reviewed/osaka-city/assembly/assembly_evidence_packets.json";
import osakaCityVoteEvidence from "../../../data/reviewed/osaka-city/assembly/proposal_vote_evidence_packets.json";
import osakaCityExpenseEvidence from "../../../data/reviewed/osaka-city/assembly/expense_evidence_packets.json";
import osakaCityTripEvidence from "../../../data/reviewed/osaka-city/assembly/inspection_evidence_packets.json";
import osakaCitySources from "../../../data/catalog/osaka_city_assembly_sources.json";
import sakaiAssembly from "../../../data/reviewed/sakai-city/assembly/assembly_records.json";
import sakaiDisclosure from "../../../data/reviewed/sakai-city/assembly/disclosure_profiles.json";
import sakaiSessions from "../../../data/reviewed/sakai-city/assembly/sessions.json";
import sakaiProposals from "../../../data/reviewed/sakai-city/assembly/proposals.json";
import sakaiVotes from "../../../data/reviewed/sakai-city/assembly/votes.json";
import sakaiFactionVotes from "../../../data/reviewed/sakai-city/assembly/faction_votes.json";
import sakaiExpenses from "../../../data/reviewed/sakai-city/assembly/political_activity_expenses.json";
import sakaiTrips from "../../../data/reviewed/sakai-city/assembly/inspection_trips.json";
import sakaiAssemblyEvidence from "../../../data/reviewed/sakai-city/assembly/assembly_evidence_packets.json";
import sakaiVoteEvidence from "../../../data/reviewed/sakai-city/assembly/proposal_vote_evidence_packets.json";
import sakaiExpenseEvidence from "../../../data/reviewed/sakai-city/assembly/expense_evidence_packets.json";
import sakaiTripEvidence from "../../../data/reviewed/sakai-city/assembly/inspection_evidence_packets.json";
import sakaiSources from "../../../data/catalog/sakai_city_assembly_sources.json";

import hokkaidoAssembly from "../../../data/reviewed/hokkaido-prefecture/assembly/assembly_records.json";
import hokkaidoDisclosure from "../../../data/reviewed/hokkaido-prefecture/assembly/disclosure_profiles.json";
import hokkaidoSessions from "../../../data/reviewed/hokkaido-prefecture/assembly/sessions.json";
import hokkaidoProposals from "../../../data/reviewed/hokkaido-prefecture/assembly/proposals.json";
import hokkaidoVotes from "../../../data/reviewed/hokkaido-prefecture/assembly/votes.json";
import hokkaidoFactionVotes from "../../../data/reviewed/hokkaido-prefecture/assembly/faction_votes.json";
import hokkaidoExpenses from "../../../data/reviewed/hokkaido-prefecture/assembly/political_activity_expenses.json";
import hokkaidoTrips from "../../../data/reviewed/hokkaido-prefecture/assembly/inspection_trips.json";
import hokkaidoAssemblyEvidence from "../../../data/reviewed/hokkaido-prefecture/assembly/assembly_evidence_packets.json";
import hokkaidoVoteEvidence from "../../../data/reviewed/hokkaido-prefecture/assembly/proposal_vote_evidence_packets.json";
import hokkaidoExpenseEvidence from "../../../data/reviewed/hokkaido-prefecture/assembly/expense_evidence_packets.json";
import hokkaidoTripEvidence from "../../../data/reviewed/hokkaido-prefecture/assembly/inspection_evidence_packets.json";
import hokkaidoSources from "../../../data/catalog/hokkaido_assembly_sources.json";
import sapporoAssembly from "../../../data/reviewed/sapporo-city/assembly/assembly_records.json";
import sapporoDisclosure from "../../../data/reviewed/sapporo-city/assembly/disclosure_profiles.json";
import sapporoSessions from "../../../data/reviewed/sapporo-city/assembly/sessions.json";
import sapporoProposals from "../../../data/reviewed/sapporo-city/assembly/proposals.json";
import sapporoVotes from "../../../data/reviewed/sapporo-city/assembly/votes.json";
import sapporoFactionVotes from "../../../data/reviewed/sapporo-city/assembly/faction_votes.json";
import sapporoExpenses from "../../../data/reviewed/sapporo-city/assembly/political_activity_expenses.json";
import sapporoTrips from "../../../data/reviewed/sapporo-city/assembly/inspection_trips.json";
import sapporoAssemblyEvidence from "../../../data/reviewed/sapporo-city/assembly/assembly_evidence_packets.json";
import sapporoVoteEvidence from "../../../data/reviewed/sapporo-city/assembly/proposal_vote_evidence_packets.json";
import sapporoExpenseEvidence from "../../../data/reviewed/sapporo-city/assembly/expense_evidence_packets.json";
import sapporoTripEvidence from "../../../data/reviewed/sapporo-city/assembly/inspection_evidence_packets.json";
import sapporoSources from "../../../data/catalog/sapporo_assembly_sources.json";
import asahikawaAssembly from "../../../data/reviewed/asahikawa-city/assembly/assembly_records.json";
import asahikawaDisclosure from "../../../data/reviewed/asahikawa-city/assembly/disclosure_profiles.json";
import asahikawaSessions from "../../../data/reviewed/asahikawa-city/assembly/sessions.json";
import asahikawaProposals from "../../../data/reviewed/asahikawa-city/assembly/proposals.json";
import asahikawaVotes from "../../../data/reviewed/asahikawa-city/assembly/votes.json";
import asahikawaFactionVotes from "../../../data/reviewed/asahikawa-city/assembly/faction_votes.json";
import asahikawaExpenses from "../../../data/reviewed/asahikawa-city/assembly/political_activity_expenses.json";
import asahikawaTrips from "../../../data/reviewed/asahikawa-city/assembly/inspection_trips.json";
import asahikawaAssemblyEvidence from "../../../data/reviewed/asahikawa-city/assembly/assembly_evidence_packets.json";
import asahikawaVoteEvidence from "../../../data/reviewed/asahikawa-city/assembly/proposal_vote_evidence_packets.json";
import asahikawaExpenseEvidence from "../../../data/reviewed/asahikawa-city/assembly/expense_evidence_packets.json";
import asahikawaTripEvidence from "../../../data/reviewed/asahikawa-city/assembly/inspection_evidence_packets.json";
import asahikawaSources from "../../../data/catalog/asahikawa_city_assembly_sources.json";

import aichiAssembly from "../../../data/reviewed/aichi-prefecture/assembly/assembly_records.json";
import aichiDisclosure from "../../../data/reviewed/aichi-prefecture/assembly/disclosure_profiles.json";
import aichiSessions from "../../../data/reviewed/aichi-prefecture/assembly/sessions.json";
import aichiProposals from "../../../data/reviewed/aichi-prefecture/assembly/proposals.json";
import aichiVotes from "../../../data/reviewed/aichi-prefecture/assembly/votes.json";
import aichiFactionVotes from "../../../data/reviewed/aichi-prefecture/assembly/faction_votes.json";
import aichiExpenses from "../../../data/reviewed/aichi-prefecture/assembly/political_activity_expenses.json";
import aichiAssemblyEvidence from "../../../data/reviewed/aichi-prefecture/assembly/assembly_evidence_packets.json";
import aichiVoteEvidence from "../../../data/reviewed/aichi-prefecture/assembly/proposal_vote_evidence_packets.json";
import aichiExpenseEvidence from "../../../data/reviewed/aichi-prefecture/assembly/expense_evidence_packets.json";
import aichiTrips from "../../../data/reviewed/aichi-prefecture/assembly/inspection_trips.json";
import aichiTripEvidence from "../../../data/reviewed/aichi-prefecture/assembly/inspection_evidence_packets.json";
import aichiSources from "../../../data/catalog/aichi_assembly_sources.json";
import nagoyaAssembly from "../../../data/reviewed/nagoya-city/assembly/assembly_records.json";
import nagoyaDisclosure from "../../../data/reviewed/nagoya-city/assembly/disclosure_profiles.json";
import nagoyaSessions from "../../../data/reviewed/nagoya-city/assembly/sessions.json";
import nagoyaProposals from "../../../data/reviewed/nagoya-city/assembly/proposals.json";
import nagoyaVotes from "../../../data/reviewed/nagoya-city/assembly/votes.json";
import nagoyaFactionVotes from "../../../data/reviewed/nagoya-city/assembly/faction_votes.json";
import nagoyaExpenses from "../../../data/reviewed/nagoya-city/assembly/political_activity_expenses.json";
import nagoyaAssemblyEvidence from "../../../data/reviewed/nagoya-city/assembly/assembly_evidence_packets.json";
import nagoyaVoteEvidence from "../../../data/reviewed/nagoya-city/assembly/proposal_vote_evidence_packets.json";
import nagoyaExpenseEvidence from "../../../data/reviewed/nagoya-city/assembly/expense_evidence_packets.json";
import nagoyaSources from "../../../data/catalog/nagoya_assembly_sources.json";
import toyotaAssembly from "../../../data/reviewed/toyota-city/assembly/assembly_records.json";
import toyotaDisclosure from "../../../data/reviewed/toyota-city/assembly/disclosure_profiles.json";
import toyotaSessions from "../../../data/reviewed/toyota-city/assembly/sessions.json";
import toyotaProposals from "../../../data/reviewed/toyota-city/assembly/proposals.json";
import toyotaVotes from "../../../data/reviewed/toyota-city/assembly/votes.json";
import toyotaFactionVotes from "../../../data/reviewed/toyota-city/assembly/faction_votes.json";
import toyotaExpenses from "../../../data/reviewed/toyota-city/assembly/political_activity_expenses.json";
import toyotaAssemblyEvidence from "../../../data/reviewed/toyota-city/assembly/assembly_evidence_packets.json";
import toyotaVoteEvidence from "../../../data/reviewed/toyota-city/assembly/proposal_vote_evidence_packets.json";
import toyotaExpenseEvidence from "../../../data/reviewed/toyota-city/assembly/expense_evidence_packets.json";
import toyotaTrips from "../../../data/reviewed/toyota-city/assembly/inspection_trips.json";
import toyotaTripEvidence from "../../../data/reviewed/toyota-city/assembly/inspection_evidence_packets.json";
import toyotaSources from "../../../data/catalog/toyota_city_assembly_sources.json";

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


// Kanagawa cluster: prefectural assembly, Yokohama City Assembly and Kawasaki City Council.
import kanagawaAssembly from "../../../data/reviewed/kanagawa-prefecture/assembly/assembly_records.json";
import kanagawaDisclosure from "../../../data/reviewed/kanagawa-prefecture/assembly/disclosure_profiles.json";
import kanagawaSessions from "../../../data/reviewed/kanagawa-prefecture/assembly/sessions.json";
import kanagawaProposals from "../../../data/reviewed/kanagawa-prefecture/assembly/proposals.json";
import kanagawaVotes from "../../../data/reviewed/kanagawa-prefecture/assembly/votes.json";
import kanagawaFactionVotes from "../../../data/reviewed/kanagawa-prefecture/assembly/faction_votes.json";
import kanagawaExpenses from "../../../data/reviewed/kanagawa-prefecture/assembly/political_activity_expenses.json";
import kanagawaTrips from "../../../data/reviewed/kanagawa-prefecture/assembly/inspection_trips.json";
import kanagawaAssemblyEvidence from "../../../data/reviewed/kanagawa-prefecture/assembly/assembly_evidence_packets.json";
import kanagawaVoteEvidence from "../../../data/reviewed/kanagawa-prefecture/assembly/proposal_vote_evidence_packets.json";
import kanagawaExpenseEvidence from "../../../data/reviewed/kanagawa-prefecture/assembly/expense_evidence_packets.json";
import kanagawaTripEvidence from "../../../data/reviewed/kanagawa-prefecture/assembly/inspection_evidence_packets.json";
import kanagawaSources from "../../../data/catalog/kanagawa_prefecture_assembly_sources.json";

import yokohamaAssembly from "../../../data/reviewed/yokohama-city/assembly/assembly_records.json";
import yokohamaDisclosure from "../../../data/reviewed/yokohama-city/assembly/disclosure_profiles.json";
import yokohamaSessions from "../../../data/reviewed/yokohama-city/assembly/sessions.json";
import yokohamaProposals from "../../../data/reviewed/yokohama-city/assembly/proposals.json";
import yokohamaVotes from "../../../data/reviewed/yokohama-city/assembly/votes.json";
import yokohamaFactionVotes from "../../../data/reviewed/yokohama-city/assembly/faction_votes.json";
import yokohamaExpenses from "../../../data/reviewed/yokohama-city/assembly/political_activity_expenses.json";
import yokohamaTrips from "../../../data/reviewed/yokohama-city/assembly/inspection_trips.json";
import yokohamaAssemblyEvidence from "../../../data/reviewed/yokohama-city/assembly/assembly_evidence_packets.json";
import yokohamaVoteEvidence from "../../../data/reviewed/yokohama-city/assembly/proposal_vote_evidence_packets.json";
import yokohamaExpenseEvidence from "../../../data/reviewed/yokohama-city/assembly/expense_evidence_packets.json";
import yokohamaTripEvidence from "../../../data/reviewed/yokohama-city/assembly/inspection_evidence_packets.json";
import yokohamaSources from "../../../data/catalog/yokohama_city_assembly_sources.json";

import kawasakiAssembly from "../../../data/reviewed/kawasaki-city/assembly/assembly_records.json";
import kawasakiDisclosure from "../../../data/reviewed/kawasaki-city/assembly/disclosure_profiles.json";
import kawasakiSessions from "../../../data/reviewed/kawasaki-city/assembly/sessions.json";
import kawasakiProposals from "../../../data/reviewed/kawasaki-city/assembly/proposals.json";
import kawasakiVotes from "../../../data/reviewed/kawasaki-city/assembly/votes.json";
import kawasakiFactionVotes from "../../../data/reviewed/kawasaki-city/assembly/faction_votes.json";
import kawasakiExpenses from "../../../data/reviewed/kawasaki-city/assembly/political_activity_expenses.json";
import kawasakiTrips from "../../../data/reviewed/kawasaki-city/assembly/inspection_trips.json";
import kawasakiAssemblyEvidence from "../../../data/reviewed/kawasaki-city/assembly/assembly_evidence_packets.json";
import kawasakiVoteEvidence from "../../../data/reviewed/kawasaki-city/assembly/proposal_vote_evidence_packets.json";
import kawasakiExpenseEvidence from "../../../data/reviewed/kawasaki-city/assembly/expense_evidence_packets.json";
import kawasakiTripEvidence from "../../../data/reviewed/kawasaki-city/assembly/inspection_evidence_packets.json";
import kawasakiSources from "../../../data/catalog/kawasaki_city_assembly_sources.json";

export type AssemblySlug = "osaka-prefecture" | "osaka-city" | "sakai-city" | "hokkaido-prefecture" | "sapporo-city" | "asahikawa-city" | "fukuoka-prefecture" | "fukuoka-city" | "kitakyushu-city" | "aichi-prefecture" | "nagoya-city" | "toyota-city" | "kanagawa-prefecture" | "yokohama-city" | "kawasaki-city" | "saitama-prefecture" | "saitama-city" | "kawaguchi-city";
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
  submitted_by: string; decided_at: string | null; submitted_at?: string | null;
  outcome: string; related_fiscal_record_ids: string[]; sources: string[];
};
export type Vote = {
  id: string; proposal_id: string; member_vote_availability: string;
  totals: { for?: number; against?: number } | null;
  /** Officially published per-member votes, never reconstructed from factions. */
  member_votes?: { member_name: string; position: string }[];
  method?: string;
  item_scope?: string | null;
  vote_date: string | null; sources: string[];
};
export type FactionVote = {
  id: string; vote_id: string; faction_name: string; member_count: number | null;
  position: string; for_count?: number | null; against_count?: number | null; sources: string[];
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
  "saitama-prefecture": registry(
    saitamaPrefAssembly, saitamaPrefDisclosure, saitamaPrefSessions, saitamaPrefProposals.map(proposal => ({ related_fiscal_record_ids: [], ...proposal })), saitamaPrefVotes,
    saitamaPrefFactionVotes, saitamaPrefExpenses.map(expense => ({ breakdown: [], ...expense })), saitamaPrefTrips,
    [...saitamaPrefAssemblyEvidence, ...saitamaPrefVoteEvidence, ...saitamaPrefExpenseEvidence, ...saitamaPrefTripEvidence],
    saitamaPrefSources.records,
  ),
  "saitama-city": registry(
    saitamaCityAssembly, saitamaCityDisclosure, saitamaCitySessions, saitamaCityProposals, saitamaCityVotes,
    saitamaCityFactionVotes, saitamaCityExpenses.map(expense => ({ breakdown: [], ...expense })), saitamaCityTrips,
    [...saitamaCityAssemblyEvidence, ...saitamaCityVoteEvidence, ...saitamaCityExpenseEvidence, ...saitamaCityTripEvidence],
    saitamaCitySources.records,
  ),
  "kawaguchi-city": registry(
    kawaguchiAssembly, kawaguchiDisclosure, kawaguchiSessions, kawaguchiProposals, kawaguchiVotes,
    kawaguchiFactionVotes, kawaguchiExpenses.map(expense => ({ breakdown: [], ...expense })), kawaguchiTrips,
    [...kawaguchiAssemblyEvidence, ...kawaguchiVoteEvidence, ...kawaguchiExpenseEvidence, ...kawaguchiTripEvidence],
    kawaguchiSources.records,
  ),

  "osaka-prefecture": registry(
    osakaPrefAssembly, osakaPrefDisclosure, osakaPrefSessions, osakaPrefProposals, osakaPrefVotes,
    osakaPrefFactionVotes, osakaPrefExpenses, osakaPrefTrips,
    [...osakaPrefAssemblyEvidence, ...osakaPrefVoteEvidence, ...osakaPrefExpenseEvidence, ...osakaPrefTripEvidence],
    osakaPrefSources.records,
  ),
  "osaka-city": registry(
    osakaCityAssembly, osakaCityDisclosure, osakaCitySessions, osakaCityProposals, osakaCityVotes,
    osakaCityFactionVotes, osakaCityExpenses, osakaCityTrips,
    [...osakaCityAssemblyEvidence, ...osakaCityVoteEvidence, ...osakaCityExpenseEvidence, ...osakaCityTripEvidence],
    osakaCitySources.records,
  ),
  "sakai-city": registry(
    sakaiAssembly, sakaiDisclosure, sakaiSessions, sakaiProposals, sakaiVotes,
    sakaiFactionVotes, sakaiExpenses, sakaiTrips,
    [...sakaiAssemblyEvidence, ...sakaiVoteEvidence, ...sakaiExpenseEvidence, ...sakaiTripEvidence],
    sakaiSources.records,
  ),
  "hokkaido-prefecture": registry(
    hokkaidoAssembly, hokkaidoDisclosure, hokkaidoSessions, hokkaidoProposals, hokkaidoVotes,
    hokkaidoFactionVotes, hokkaidoExpenses.map((expense) => ({ breakdown: [], ...expense })), hokkaidoTrips,
    [...hokkaidoAssemblyEvidence, ...hokkaidoVoteEvidence, ...hokkaidoExpenseEvidence, ...hokkaidoTripEvidence],
    hokkaidoSources.records,
  ),
  "sapporo-city": registry(
    sapporoAssembly, sapporoDisclosure, sapporoSessions, sapporoProposals, sapporoVotes,
    sapporoFactionVotes, sapporoExpenses, sapporoTrips,
    [...sapporoAssemblyEvidence, ...sapporoVoteEvidence, ...sapporoExpenseEvidence, ...sapporoTripEvidence],
    sapporoSources.records,
  ),
  "asahikawa-city": registry(
    asahikawaAssembly, asahikawaDisclosure, asahikawaSessions, asahikawaProposals, asahikawaVotes,
    asahikawaFactionVotes, asahikawaExpenses, asahikawaTrips,
    [...asahikawaAssemblyEvidence, ...asahikawaVoteEvidence, ...asahikawaExpenseEvidence, ...asahikawaTripEvidence],
    asahikawaSources.records,
  ),
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
  "aichi-prefecture": registry(
    aichiAssembly, aichiDisclosure, aichiSessions, aichiProposals, aichiVotes,
    aichiFactionVotes, aichiExpenses, aichiTrips,
    [...aichiAssemblyEvidence, ...aichiVoteEvidence, ...aichiExpenseEvidence, ...aichiTripEvidence],
    aichiSources.records,
  ),
  "nagoya-city": registry(
    nagoyaAssembly, nagoyaDisclosure, nagoyaSessions, nagoyaProposals, nagoyaVotes,
    nagoyaFactionVotes, nagoyaExpenses, [],
    [...nagoyaAssemblyEvidence, ...nagoyaVoteEvidence, ...nagoyaExpenseEvidence],
    nagoyaSources.records,
  ),
  "toyota-city": registry(
    toyotaAssembly, toyotaDisclosure, toyotaSessions, toyotaProposals, toyotaVotes,
    toyotaFactionVotes, toyotaExpenses, toyotaTrips,
    [...toyotaAssemblyEvidence, ...toyotaVoteEvidence, ...toyotaExpenseEvidence, ...toyotaTripEvidence],
    toyotaSources.records,
  ),
  "kanagawa-prefecture": registry(
    kanagawaAssembly, kanagawaDisclosure, kanagawaSessions, kanagawaProposals, kanagawaVotes,
    kanagawaFactionVotes, kanagawaExpenses, kanagawaTrips,
    [...kanagawaAssemblyEvidence, ...kanagawaVoteEvidence, ...kanagawaExpenseEvidence, ...kanagawaTripEvidence],
    kanagawaSources.records,
  ),
  "yokohama-city": registry(
    yokohamaAssembly, yokohamaDisclosure, yokohamaSessions, yokohamaProposals, yokohamaVotes,
    yokohamaFactionVotes, yokohamaExpenses, yokohamaTrips,
    [...yokohamaAssemblyEvidence, ...yokohamaVoteEvidence, ...yokohamaExpenseEvidence, ...yokohamaTripEvidence],
    yokohamaSources.records,
  ),
  "kawasaki-city": registry(
    kawasakiAssembly, kawasakiDisclosure, kawasakiSessions, kawasakiProposals, kawasakiVotes,
    kawasakiFactionVotes, kawasakiExpenses, kawasakiTrips,
    [...kawasakiAssemblyEvidence, ...kawasakiVoteEvidence, ...kawasakiExpenseEvidence, ...kawasakiTripEvidence],
    kawasakiSources.records,
  ),
};
export const assemblySlugs: AssemblySlug[] = [
  "osaka-prefecture", "osaka-city", "sakai-city",
  "hokkaido-prefecture", "sapporo-city", "asahikawa-city",
  "fukuoka-prefecture", "fukuoka-city", "kitakyushu-city",
  "aichi-prefecture", "nagoya-city", "toyota-city",
  "kanagawa-prefecture", "yokohama-city", "kawasaki-city",
  "saitama-prefecture", "saitama-city", "kawaguchi-city",
];
export function isAssemblySlug(slug: string): slug is AssemblySlug {
  return Object.prototype.hasOwnProperty.call(assemblies, slug);
}
export function evidenceFor(registry: Registry, id: string): Evidence[] {
  return registry.evidence.filter((packet) => packet.subject_id === id);
}
