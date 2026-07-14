import catalog from "../../../data/catalog/official_sources.json";

export type MunicipalityKey =
  | "fukuoka-prefecture"
  | "fukuoka-city"
  | "kitakyushu-city";

export type SourceRecord = {
  id: string;
  municipality_key: MunicipalityKey;
  organization: string;
  category: string;
  title: string;
  url: string;
  source_kind: "landing_page" | "document" | "dataset" | "search_system";
  availability: "published" | "not_published" | "not_found" | "restricted" | "unknown";
  indexed_at: string;
  review_status: "verified" | "reviewed" | "extracted" | "inferred" | "missing";
  confidence: "high" | "medium" | "low" | "not_assessable";
  notes: string;
};

export const municipalityMeta: Record<
  MunicipalityKey,
  {
    name: string;
    type: string;
    summary: string;
    status: "資料索引中" | "当初予算公開";
    href: string | null;
  }
> = {
  "fukuoka-prefecture": {
    name: "福岡県",
    type: "都道府県",
    summary: "県財政、重点政策、知事公約、県議会を一つの流れで検証します。",
    status: "当初予算公開",
    href: "/municipalities/fukuoka-prefecture",
  },
  "fukuoka-city": {
    name: "福岡市",
    type: "政令指定都市",
    summary: "成長都市の財政、主要プロジェクト、市長公約、市議会を整理します。",
    status: "資料索引中",
    href: null,
  },
  "kitakyushu-city": {
    name: "北九州市",
    type: "政令指定都市",
    summary: "人口・産業構造の変化と政策、財政、市長、市議会を接続します。",
    status: "資料索引中",
    href: null,
  },
};

export const sourceCatalog = catalog.records as SourceRecord[];

export const catalogStats = {
  municipalities: Object.keys(municipalityMeta).length,
  officialSources: sourceCatalog.length,
  reviewedSources: sourceCatalog.filter((source) => source.review_status === "reviewed").length,
  publishedEvaluations: 0,
  publishedFiscalValues: 2,
  updatedAt: catalog.updated_at,
};

export function sourcesForMunicipality(key: MunicipalityKey) {
  return sourceCatalog.filter((source) => source.municipality_key === key);
}
