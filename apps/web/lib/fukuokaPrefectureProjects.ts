import selectionCatalog from "../../../data/catalog/fukuoka_priority_project_selection.json";
import evidencePackets from "../../../data/reviewed/fukuoka-prefecture/project_evidence_packets.json";
import kpis from "../../../data/reviewed/fukuoka-prefecture/project_kpis.json";
import projects from "../../../data/reviewed/fukuoka-prefecture/projects.json";

import type { EvidencePacket } from "./finance";

export type ProjectBudgetRecord = {
  kind: "initial_budget" | "revised_budget" | "execution" | "settlement";
  amount_yen: number | null;
  fiscal_year: number;
  note: string | null;
};

export type ProjectKpiSummary = {
  name: string;
  unit: string;
  baseline: number | string | null;
  target: number | string | null;
  actual: number | string | null;
  assessment: string;
};

export type OfficialEvaluation = {
  rating: string;
  direction: string | null;
  note: string | null;
};

export type ProjectRecord = {
  id: string;
  series_id: string;
  municipality_id: string;
  fiscal_year: number;
  official_title: string;
  plain_title: string;
  purpose: string;
  target_population: string | null;
  policy_area: string;
  responsible_department: string | null;
  parent_policy: string | null;
  official_evaluation: OfficialEvaluation | null;
  related_promise_ids: string[];
  budget_records: ProjectBudgetRecord[];
  kpis: ProjectKpiSummary[];
  review_status: string;
  confidence: string;
  sources: string[];
};

export type KpiObservation = {
  period: string;
  value: number | string | null;
  status: string;
  source_ids?: string[];
};

export type KpiRecord = {
  id: string;
  project_id: string;
  name: string;
  definition: string;
  unit: string;
  direction: string;
  baseline?: KpiObservation | null;
  target?: KpiObservation | null;
  actuals?: KpiObservation[];
  assessment: string;
  causality_note: string | null;
  review_status: string;
  confidence: string;
  sources: string[];
};

export type ProjectSeries = {
  seriesId: string;
  officialTitle: string;
  projects: ProjectRecord[];
};

export const fukuokaPrefectureProjectData = {
  projects: projects as ProjectRecord[],
  kpis: kpis as KpiRecord[],
  evidencePackets: evidencePackets as EvidencePacket[],
  selection: selectionCatalog,
};

/** All annual project records registered for Fukuoka Prefecture, in file order. */
export function fukuokaPrefectureProjects(): ProjectRecord[] {
  return fukuokaPrefectureProjectData.projects;
}

/** Project series (the same project across fiscal years), grouped by series_id. */
export function fukuokaPrefectureProjectSeries(): ProjectSeries[] {
  const bySeries = new Map<string, ProjectRecord[]>();
  for (const project of fukuokaPrefectureProjectData.projects) {
    const list = bySeries.get(project.series_id) ?? [];
    list.push(project);
    bySeries.set(project.series_id, list);
  }
  return [...bySeries.entries()].map(([seriesId, seriesProjects]) => ({
    seriesId,
    officialTitle: seriesProjects[0].official_title,
    projects: [...seriesProjects].sort((a, b) => a.fiscal_year - b.fiscal_year),
  }));
}

/** Annual records that belong to one project series, ordered by fiscal year. */
export function projectsForSeries(seriesId: string): ProjectRecord[] {
  return fukuokaPrefectureProjectData.projects
    .filter((project) => project.series_id === seriesId)
    .sort((a, b) => a.fiscal_year - b.fiscal_year);
}

/** Standalone KPI records linked to one annual project record. */
export function kpisForProject(projectId: string): KpiRecord[] {
  return fukuokaPrefectureProjectData.kpis.filter((kpi) => kpi.project_id === projectId);
}

/** Evidence packet for one annual project record, if registered. */
export function evidenceForProject(projectId: string) {
  return fukuokaPrefectureProjectData.evidencePackets.find(
    (packet) => packet.subject_id === projectId,
  );
}
