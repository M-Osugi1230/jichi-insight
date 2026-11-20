import hokkaidoFinanceCatalog from "../../../data/catalog/hokkaido_prefecture_finance_sources.json";
import kanagawaFinanceCatalog from "../../../data/catalog/kanagawa_prefecture_finance_sources.json";
import saitamaFinanceCatalog from "../../../data/catalog/saitama_prefecture_finance_sources.json";
import aichiFinanceCatalog from "../../../data/catalog/aichi_prefecture_finance_sources.json";
import assemblyCatalog from "../../../data/catalog/fukuoka_assembly_sources.json";
import cityFinanceCatalog from "../../../data/catalog/fukuoka_city_finance_sources.json";
import financeCatalog from "../../../data/catalog/fukuoka_finance_sources.json";
import kitakyushuFinanceCatalog from "../../../data/catalog/kitakyushu_finance_sources.json";
import officialCatalog from "../../../data/catalog/official_sources.json";

export type MunicipalityKey =
  | "hokkaido-prefecture"
  | "kawasaki-city"
  | "kanagawa-prefecture"
  | "yokohama-city"
  | "osaka-prefecture"
  | "osaka-city"
  | "sakai-city"
  | "aichi-prefecture"
  | "fukuoka-prefecture"
  | "fukuoka-city"
  | "kitakyushu-city"
  | "nagoya-city"
  | "toyota-city"
  | "sapporo-city"
  | "asahikawa-city"
  | "saitama-prefecture"
  | "saitama-city";

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
    status: "資料索引中" | "財政データ公開";
    href: string | null;
    fiscalSummary: string;
  }
> = {
  "osaka-prefecture": {
    name: "大阪府", type: "都道府県",
    summary: "大阪府の計画・財政・重点事業と知事の公式選挙公報に基づく公約7件を確認します。",
    status: "財政データ公開", href: "/municipalities/osaka",
    fiscalSummary: "Reviewed 財政レコード（大阪クラスター）",
  },
  "osaka-city": {
    name: "大阪市", type: "政令指定都市",
    summary: "大阪市の計画・財政・重点事業と市長の公約原文5件を公式資料で確認します。",
    status: "財政データ公開", href: "/municipalities/osaka-city",
    fiscalSummary: "Reviewed 財政データ（汎用市ページ）",
  },
  "sakai-city": {
    name: "堺市", type: "政令指定都市",
    summary: "計画・財政・重点事業と市長の現任期を確認します。公約原文は未登録です。",
    status: "財政データ公開", href: "/municipalities/sakai-city",
    fiscalSummary: "Reviewed 財政データ（汎用市ページ）",
  },
  "kanagawa-prefecture": {
    name: "神奈川県", type: "都道府県",
    summary: "新かながわグランドデザイン、2026年度成立後当初予算、2022〜2024年度の普通会計決算、黒岩祐治知事の現任期・公約33件、県議会を確認します。",
    status: "財政データ公開", href: "/municipalities/kanagawa-prefecture",
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
  },
  "saitama-prefecture": {
    name: "埼玉県", type: "都道府県",
    summary: "埼玉県5か年計画、2026年度成立後当初予算、2022〜2024年度の普通会計決算と大野元裕知事の現任期を確認します。自治体別ページは準備中です。",
    status: "財政データ公開", href: null,
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
  },
  "saitama-city": {
    name: "さいたま市", type: "政令指定都市",
    summary: "計画・財政・重点事業に加え、清水勇人市長の任期と Reviewed 公約12件を公式出典で確認します。自治体別ページは準備中です。",
    status: "財政データ公開", href: null,
    fiscalSummary: "Reviewed 54項目（財政レコード3件・決算51件）",
  },
  "kawasaki-city": {
    name: "川崎市", type: "政令指定都市",
    summary: "計画・財政・重点事業に加え、福田紀彦市長の任期と Reviewed 公約13件を公式出典で確認します。自治体別ページは準備中です。",
    status: "財政データ公開", href: null,
    fiscalSummary: "Reviewed 財政レコード3件",
  },
  "yokohama-city": {
    name: "横浜市", type: "政令指定都市",
    summary: "横浜市中期計画2026～2029、2026年度成立後当初予算と原澤敦美市長の現任期・公約原文12件を公式資料で確認します。",
    status: "財政データ公開", href: "/municipalities/yokohama-city",
    fiscalSummary: "Reviewed 財政データ（汎用市ページ）",
  },
  "hokkaido-prefecture": {
    name: "北海道",
    type: "都道府県",
    summary: "北海道総合計画、2026年度成立後当初予算、3年度の普通会計決算と鈴木直道知事の現任期を確認します。",
    status: "財政データ公開",
    href: "/municipalities/hokkaido-prefecture",
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
  },
  "sapporo-city": {
    name: "札幌市",
    type: "政令指定都市",
    summary: "計画・財政・重点事業に加え、秋元克広市長の任期と Reviewed 公約13件を公式出典で確認します。",
    status: "財政データ公開",
    href: "/municipalities/sapporo-city",
    fiscalSummary: "Reviewed 財政データ（汎用市ページ）",
  },
  "asahikawa-city": {
    name: "旭川市",
    type: "中核市",
    summary: "計画・財政・重点事業と今津寛介市長の任期を確認します。公約原文は未登録であり、不存在を意味しません。",
    status: "財政データ公開",
    href: "/municipalities/asahikawa-city",
    fiscalSummary: "Reviewed 財政データ（汎用市ページ）",
  },
  "aichi-prefecture": {
    name: "愛知県",
    type: "都道府県",
    summary: "あいちビジョンの政策指標と、知事の任期・一次資料を確認します。",
    status: "財政データ公開",
    href: "/municipalities/aichi-prefecture",
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
  },
  "fukuoka-prefecture": {
    name: "福岡県",
    type: "都道府県",
    summary: "県財政、重点政策、知事公約、県議会を一つの流れで検証します。",
    status: "財政データ公開",
    href: "/municipalities/fukuoka-prefecture",
    fiscalSummary: "Reviewed 13項目",
  },
  "fukuoka-city": {
    name: "福岡市",
    type: "政令指定都市",
    summary: "成長都市の財政、主要プロジェクト、市長公約、市議会を整理します。",
    status: "財政データ公開",
    href: "/municipalities/fukuoka-city",
    fiscalSummary: "Reviewed 4項目",
  },
  "kitakyushu-city": {
    name: "北九州市",
    type: "政令指定都市",
    summary: "人口・産業構造の変化と政策、財政、市長、市議会を接続します。",
    status: "財政データ公開",
    href: "/municipalities/kitakyushu-city",
    fiscalSummary: "Reviewed 5項目",
  },
  "nagoya-city": {
    name: "名古屋市",
    type: "政令指定都市",
    summary: "財政、重点事業、市長公約を一次資料で確認します。",
    status: "財政データ公開",
    href: "/municipalities/nagoya-city",
    fiscalSummary: "Reviewed 3項目（当初予算1件・決算2件）",
  },
  "toyota-city": {
    name: "豊田市",
    type: "中核市",
    summary: "財政、重点事業、市長の任期を一次資料で確認します。",
    status: "財政データ公開",
    href: "/municipalities/toyota-city",
    fiscalSummary: "Reviewed 3項目（当初予算1件・決算2件）",
  },
};

export const sourceCatalog = [
  ...(hokkaidoFinanceCatalog.records as SourceRecord[]),
  ...(kanagawaFinanceCatalog.records as SourceRecord[]),
  ...(saitamaFinanceCatalog.records as SourceRecord[]),
  ...(aichiFinanceCatalog.records as SourceRecord[]),
  ...(officialCatalog.records as SourceRecord[]),
  ...(financeCatalog.records as SourceRecord[]),
  ...(cityFinanceCatalog.records as SourceRecord[]),
  ...(kitakyushuFinanceCatalog.records as SourceRecord[]),
  ...(assemblyCatalog.records as SourceRecord[]),
];

export const catalogStats = {
  municipalities: Object.keys(municipalityMeta).length,
  officialSources: sourceCatalog.length,
  reviewedSources: sourceCatalog.filter((source) => source.review_status === "reviewed").length,
  publishedEvaluations: 0,
  publishedFiscalValues: 22,
  reviewedAssemblyActivities: 3,
  updatedAt: assemblyCatalog.updated_at,
};

export function sourcesForMunicipality(key: MunicipalityKey) {
  return sourceCatalog.filter((source) => source.municipality_key === key);
}
