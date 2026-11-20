import osakaProjectSources from "../../../data/catalog/osaka_project_sources.json";
import osakaCityProjectSources from "../../../data/catalog/osaka_city_project_sources.json";
import sakaiProjectSources from "../../../data/catalog/sakai_project_sources.json";
import osakaSelection from "../../../data/catalog/osaka_priority_project_selection.json";
import osakaCitySelection from "../../../data/catalog/osaka_city_priority_project_selection.json";
import sakaiSelection from "../../../data/catalog/sakai_priority_project_selection.json";
import osakaProjects from "../../../data/reviewed/osaka-prefecture/projects.json";
import osakaKpis from "../../../data/reviewed/osaka-prefecture/project_kpis.json";
import osakaEvidence from "../../../data/reviewed/osaka-prefecture/project_evidence_packets.json";
import osakaCityProjects from "../../../data/reviewed/osaka-city/projects.json";
import osakaCityKpis from "../../../data/reviewed/osaka-city/project_kpis.json";
import osakaCityEvidence from "../../../data/reviewed/osaka-city/project_evidence_packets.json";
import sakaiProjects from "../../../data/reviewed/sakai-city/projects.json";
import sakaiKpis from "../../../data/reviewed/sakai-city/project_kpis.json";
import sakaiEvidence from "../../../data/reviewed/sakai-city/project_evidence_packets.json";
import hokkaidoProjectSources from "../../../data/catalog/hokkaido_project_sources.json";
import sapporoProjectSources from "../../../data/catalog/sapporo_city_project_sources.json";
import asahikawaProjectSources from "../../../data/catalog/asahikawa_project_sources.json";
import hokkaidoSelection from "../../../data/catalog/hokkaido_priority_project_selection.json";
import sapporoSelection from "../../../data/catalog/sapporo_city_priority_project_selection.json";
import asahikawaSelection from "../../../data/catalog/asahikawa_priority_project_selection.json";
import hokkaidoProjects from "../../../data/reviewed/hokkaido-prefecture/projects.json";
import hokkaidoKpis from "../../../data/reviewed/hokkaido-prefecture/project_kpis.json";
import hokkaidoEvidence from "../../../data/reviewed/hokkaido-prefecture/project_evidence_packets.json";
import sapporoProjects from "../../../data/reviewed/sapporo-city/projects.json";
import sapporoKpis from "../../../data/reviewed/sapporo-city/project_kpis.json";
import sapporoEvidence from "../../../data/reviewed/sapporo-city/project_evidence_packets.json";
import asahikawaProjects from "../../../data/reviewed/asahikawa-city/projects.json";
import asahikawaKpis from "../../../data/reviewed/asahikawa-city/project_kpis.json";
import asahikawaEvidence from "../../../data/reviewed/asahikawa-city/project_evidence_packets.json";
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

export type ProjectArea = "fukuoka-prefecture" | "osaka-prefecture" | "osaka-city" | "sakai-city" | "fukuoka-city" | "kitakyushu-city" | "aichi-prefecture" | "nagoya-city" | "toyota-city" | "hokkaido-prefecture" | "sapporo-city" | "asahikawa-city";
type Selection = { updated_at?: string; population?: { description?: string; label?: string }; selection_rule?: { description?: string } | string; };
type SetOfProjects = { name: string; projects: ProjectRecord[]; kpis: KpiRecord[]; evidencePackets: EvidencePacket[]; selection: Selection };
export const projectRegistry: Record<ProjectArea, SetOfProjects> = {
  "osaka-prefecture": { name: "大阪府", projects: osakaProjects as ProjectRecord[], kpis: osakaKpis as KpiRecord[], evidencePackets: osakaEvidence as EvidencePacket[], selection: osakaSelection },
  "osaka-city": { name: "大阪市", projects: osakaCityProjects as ProjectRecord[], kpis: osakaCityKpis as KpiRecord[], evidencePackets: osakaCityEvidence as EvidencePacket[], selection: osakaCitySelection },
  "sakai-city": { name: "堺市", projects: sakaiProjects as ProjectRecord[], kpis: sakaiKpis as KpiRecord[], evidencePackets: sakaiEvidence as EvidencePacket[], selection: sakaiSelection },
  "fukuoka-prefecture": { name: "福岡県", ...fukuokaPrefectureProjectData },
  "fukuoka-city": { name: "福岡市", ...fukuokaCityProjectData },
  "kitakyushu-city": { name: "北九州市", ...kitakyushuProjectData },
  "aichi-prefecture": { name: "愛知県", projects: aichiProjects as ProjectRecord[], kpis: aichiKpis as KpiRecord[], evidencePackets: aichiEvidence as EvidencePacket[], selection: aichiSelection },
  "nagoya-city": { name: "名古屋市", projects: nagoyaProjects as ProjectRecord[], kpis: nagoyaKpis as KpiRecord[], evidencePackets: nagoyaEvidence as EvidencePacket[], selection: nagoyaSelection },
  "toyota-city": { name: "豊田市", projects: toyotaProjects as ProjectRecord[], kpis: toyotaKpis as KpiRecord[], evidencePackets: toyotaEvidence as EvidencePacket[], selection: toyotaSelection },
  "hokkaido-prefecture": { name: "北海道", projects: hokkaidoProjects as ProjectRecord[], kpis: hokkaidoKpis as KpiRecord[], evidencePackets: hokkaidoEvidence as EvidencePacket[], selection: hokkaidoSelection },
  "sapporo-city": { name: "札幌市", projects: sapporoProjects as ProjectRecord[], kpis: sapporoKpis as KpiRecord[], evidencePackets: sapporoEvidence as EvidencePacket[], selection: sapporoSelection },
  "asahikawa-city": { name: "旭川市", projects: asahikawaProjects as ProjectRecord[], kpis: asahikawaKpis as KpiRecord[], evidencePackets: asahikawaEvidence as EvidencePacket[], selection: asahikawaSelection },
};
export function isProjectArea(key: string): key is ProjectArea { return Object.prototype.hasOwnProperty.call(projectRegistry,key); }
export const projectSourceCatalog: SourceRecord[] = [...sourceCatalog,
  ...(kitakyushuProjectSources.records as SourceRecord[]),
  ...(fukuokaProjectSources.records as SourceRecord[]),
  ...(fukuokaCityProjectSources.records as SourceRecord[]),
  ...(aichiProjectSources.records as SourceRecord[]),
  ...(nagoyaProjectSources.records as SourceRecord[]),
  ...(toyotaProjectSources.records as SourceRecord[]),
  ...(hokkaidoProjectSources.records as SourceRecord[]),
  ...(sapporoProjectSources.records as SourceRecord[]),
  ...(osakaProjectSources.records as SourceRecord[]),
  ...(osakaCityProjectSources.records as SourceRecord[]),
  ...(sakaiProjectSources.records as SourceRecord[]),
  ...(asahikawaProjectSources.records as SourceRecord[])];
