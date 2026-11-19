import aichiProjectSources from "../../../data/catalog/aichi_project_sources.json";
import nagoyaProjectSources from "../../../data/catalog/nagoya_city_project_sources.json";
import toyotaProjectSources from "../../../data/catalog/toyota_project_sources.json";
import aichiSelection from "../../../data/catalog/aichi_priority_project_selection.json";
import nagoyaSelection from "../../../data/catalog/nagoya_city_priority_project_selection.json";
import toyotaSelection from "../../../data/catalog/toyota_priority_project_selection.json";
import aichiProjects from "../../../data/reviewed/aichi-prefecture/projects.json";
import aichiKpis from "../../../data/reviewed/aichi-prefecture/project_kpis.json";
import aichiEvidence from "../../../data/reviewed/aichi-prefecture/project_evidence_packets.json";
import nagoyaProjects from "../../../data/reviewed/nagoya-city/projects.json";
import nagoyaKpis from "../../../data/reviewed/nagoya-city/project_kpis.json";
import nagoyaEvidence from "../../../data/reviewed/nagoya-city/project_evidence_packets.json";
import toyotaProjects from "../../../data/reviewed/toyota-city/projects.json";
import toyotaKpis from "../../../data/reviewed/toyota-city/project_kpis.json";
import toyotaEvidence from "../../../data/reviewed/toyota-city/project_evidence_packets.json";
import kitakyushuProjectSources from "../../../data/catalog/kitakyushu_project_sources.json";
import fukuokaProjectSources from "../../../data/catalog/fukuoka_project_sources.json";
import fukuokaCityProjectSources from "../../../data/catalog/fukuoka_city_project_sources.json";
import { sourceCatalog, type SourceRecord } from "./catalog";
import { fukuokaCityProjectData } from "./fukuokaCityProjects";
import { fukuokaPrefectureProjectData } from "./fukuokaPrefectureProjects";
import { kitakyushuProjectData, type ProjectRecord, type KpiRecord } from "./kitakyushuProjects";
import type { EvidencePacket } from "./finance";

export type ProjectArea = "fukuoka-prefecture" | "fukuoka-city" | "kitakyushu-city" | "aichi-prefecture" | "nagoya-city" | "toyota-city";
type Selection = { updated_at?: string; population?: { description?: string }; selection_rule?: { description?: string }; };
type SetOfProjects = { name: string; projects: ProjectRecord[]; kpis: KpiRecord[]; evidencePackets: EvidencePacket[]; selection: Selection };
export const projectRegistry: Record<ProjectArea, SetOfProjects> = {
  "fukuoka-prefecture": { name: "福岡県", ...fukuokaPrefectureProjectData },
  "fukuoka-city": { name: "福岡市", ...fukuokaCityProjectData },
  "kitakyushu-city": { name: "北九州市", ...kitakyushuProjectData },
  "aichi-prefecture": { name: "愛知県", projects: aichiProjects as ProjectRecord[], kpis: aichiKpis as KpiRecord[], evidencePackets: aichiEvidence as EvidencePacket[], selection: aichiSelection },
  "nagoya-city": { name: "名古屋市", projects: nagoyaProjects as ProjectRecord[], kpis: nagoyaKpis as KpiRecord[], evidencePackets: nagoyaEvidence as EvidencePacket[], selection: nagoyaSelection },
  "toyota-city": { name: "豊田市", projects: toyotaProjects as ProjectRecord[], kpis: toyotaKpis as KpiRecord[], evidencePackets: toyotaEvidence as EvidencePacket[], selection: toyotaSelection },
};
export function isProjectArea(key: string): key is ProjectArea { return Object.prototype.hasOwnProperty.call(projectRegistry,key); }
export const projectSourceCatalog: SourceRecord[] = [...sourceCatalog,
  ...(kitakyushuProjectSources.records as SourceRecord[]),
  ...(fukuokaProjectSources.records as SourceRecord[]),
  ...(fukuokaCityProjectSources.records as SourceRecord[]),
  ...(aichiProjectSources.records as SourceRecord[]),
  ...(nagoyaProjectSources.records as SourceRecord[]),
  ...(toyotaProjectSources.records as SourceRecord[])];
