import kitakyushuProjectSources from "../../../data/catalog/kitakyushu_project_sources.json";
import fukuokaProjectSources from "../../../data/catalog/fukuoka_project_sources.json";
import fukuokaCityProjectSources from "../../../data/catalog/fukuoka_city_project_sources.json";
import { sourceCatalog, type SourceRecord } from "./catalog";
import { fukuokaCityProjectData } from "./fukuokaCityProjects";
import { fukuokaPrefectureProjectData } from "./fukuokaPrefectureProjects";
import { kitakyushuProjectData, type ProjectRecord, type KpiRecord } from "./kitakyushuProjects";
import type { EvidencePacket } from "./finance";

export type ProjectArea = "fukuoka-prefecture" | "fukuoka-city" | "kitakyushu-city";
type Selection = { updated_at?: string; population?: { description?: string }; selection_rule?: { description?: string }; };
type SetOfProjects = { name: string; projects: ProjectRecord[]; kpis: KpiRecord[]; evidencePackets: EvidencePacket[]; selection: Selection };
export const projectRegistry: Record<ProjectArea, SetOfProjects> = {
  "fukuoka-prefecture": { name: "福岡県", ...fukuokaPrefectureProjectData },
  "fukuoka-city": { name: "福岡市", ...fukuokaCityProjectData },
  "kitakyushu-city": { name: "北九州市", ...kitakyushuProjectData },
};
export function isProjectArea(key: string): key is ProjectArea { return Object.prototype.hasOwnProperty.call(projectRegistry,key); }
export const projectSourceCatalog: SourceRecord[] = [...sourceCatalog,
  ...(kitakyushuProjectSources.records as SourceRecord[]),
  ...(fukuokaProjectSources.records as SourceRecord[]),
  ...(fukuokaCityProjectSources.records as SourceRecord[])];
