import hokkaidoFinanceCatalog from "../../../data/catalog/hokkaido_prefecture_finance_sources.json";
import kanagawaFinanceCatalog from "../../../data/catalog/kanagawa_prefecture_finance_sources.json";
import saitamaFinanceCatalog from "../../../data/catalog/saitama_prefecture_finance_sources.json";
import chibaFinanceCatalog from "../../../data/catalog/chiba_prefecture_finance_sources.json";
import hyogoFinanceCatalog from "../../../data/catalog/hyogo_prefecture_finance_sources.json";
import miyagiFinanceCatalog from "../../../data/catalog/miyagi_prefecture_finance_sources.json";
import shizuokaFinanceCatalog from "../../../data/catalog/shizuoka_prefecture_finance_sources.json";
import hiroshimaFinanceCatalog from "../../../data/catalog/hiroshima_prefecture_finance_sources.json";
import kyotoCityFinanceCatalog from "../../../data/catalog/kyoto_city_finance_sources.json";
import niigataCityFinanceCatalog from "../../../data/catalog/niigata_city_finance_sources.json";
import kyotoFinanceCatalog from "../../../data/catalog/kyoto_prefecture_finance_sources.json";
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
  | "saitama-city"
  | "kawaguchi-city"
  | "chiba-prefecture"
  | "chiba-city"
  | "hyogo-prefecture"
  | "kobe-city"
  | "miyagi-prefecture"
  | "sendai-city"
  | "shizuoka-city"
  | "hamamatsu-city"
  | "shizuoka-prefecture"
  | "hiroshima-prefecture"
  | "hiroshima-city"
  | "kyoto-city"
  | "kyoto-prefecture"
  | "niigata-city";
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
    summary: "埼玉県5か年計画、2026年度成立後当初予算、2022〜2024年度の普通会計決算と大野元裕知事の現任期を確認します。自治体別ページで知事公約12件・重点事業10系列・県議会の公開範囲も確認できます。",
    status: "財政データ公開", href: "/municipalities/saitama-prefecture",
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
  },
  "chiba-prefecture": {
    name: "千葉県", type: "都道府県",
    summary: "千葉県総合計画 ～千葉の未来をともに創る～、2026年度成立後当初予算、2022〜2024年度の普通会計決算、熊谷俊人知事の公約25件、重点事業10系列と県議会の公開範囲を確認します。",
    status: "財政データ公開", href: "/municipalities/chiba-prefecture",
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
  },
  "chiba-city": {
    name: "千葉市", type: "政令指定都市",
    summary: "千葉市基本計画の重点事業10系列（政策単位。予算額・公式評価は未公表）に加え、神谷俊一市長の任期と Reviewed 公約25件を公式出典で確認します。自治体別ページは準備中です。",
    status: "財政データ公開", href: null,
    fiscalSummary: "Reviewed 54項目（財政レコード3件・決算51件）・重点事業10系列",
  },
  "hyogo-prefecture": {
    name: "兵庫県", type: "都道府県",
    summary: "ひょうごビジョン2050と第三期兵庫県地域創生戦略、2026年度成立後当初予算、2022〜2024年度普通会計決算、斎藤元彦知事の公約18件、取組方針項目10系列、兵庫県議会の公式公開情報を確認します。",
    status: "財政データ公開", href: "/municipalities/hyogo-prefecture",
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
  },
  "miyagi-prefecture": {
    name: "宮城県", type: "都道府県",
    summary: "新・宮城の将来ビジョン、FY2026成立後当初予算、FY2022〜2024普通会計決算、村井嘉浩知事の公約4件、施策単位10系列、宮城県議会第401回定例会の議員個人別事後表決記録を確認します。",
    status: "財政データ公開", href: "/municipalities/miyagi-prefecture",
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
  },
  "shizuoka-prefecture": {
    name: "静岡県", type: "都道府県",
    summary: "静岡県総合計画～しずおか ウェルビーイングプラン～、FY2026一般会計当初予算、普通会計決算51件、政策の柱10系列（KPI46件）、鈴木康友知事の公約9件、静岡県議会の登録議案43件を確認します。",
    status: "財政データ公開", href: "/municipalities/shizuoka-prefecture",
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
  },
  "hiroshima-prefecture": {
    name: "広島県", type: "都道府県",
    summary: "安心▷誇り▷挑戦 ひろしまビジョン（令和8年6月改定）、2026年度成立後当初予算、2022〜2024年度の普通会計決算と横田美香知事の現任期を確認します。",
    status: "財政データ公開", href: "/municipalities/hiroshima-prefecture",
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
  },
  "kyoto-prefecture": {
    name: "京都府", type: "都道府県",
    summary: "京都府総合計画（2019年策定・2022年改定）、FY2026一般会計当初予算、2022〜2024年度の普通会計決算と西脇隆俊知事の現任期を確認します。",
    status: "財政データ公開", href: "/municipalities/kyoto-prefecture",
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
  },
  "kobe-city": {
    name: "神戸市", type: "政令指定都市",
    summary: "第6次神戸市基本計画・神戸2030ビジョンの重点事業10系列（基本政策単位。予算額・公式評価は未公表）に加え、久元喜造市長の任期とReviewed公約28件、神戸市会の議案と公開状況を公式出典で確認します。",
    status: "財政データ公開", href: null,
    fiscalSummary: "Reviewed 54項目（財政レコード3件・決算51件）・重点事業10系列",
  },
  "saitama-city": {
    name: "さいたま市", type: "政令指定都市",
    summary: "計画・財政・重点事業に加え、清水勇人市長の任期と Reviewed 公約12件を公式出典で確認します。自治体別ページは準備中です。",
    status: "財政データ公開", href: null,
    fiscalSummary: "Reviewed 54項目（財政レコード3件・決算51件）",
  },
  "kawaguchi-city": {
    name: "川口市", type: "中核市",
    summary: "第6次川口市総合計画、2026年度成立後当初予算、2022〜2024年度の普通会計決算、重点事業10系列と岡村ゆり子市長の現任期・公約26件を確認します。自治体別ページは準備中です。",
    status: "財政データ公開", href: null,
    fiscalSummary: "Reviewed 54項目（当初予算3件・決算51件）",
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
  "sendai-city": {
    name: "仙台市", type: "政令指定都市",
    summary: "仙台市基本計画2021-2030・実施計画2024-2026、FY2026成立後一般会計当初予算、郡和子市長の公約4件、自己評価つき事業10系列と仙台市議会の会派別賛否を確認します。",
    status: "財政データ公開", href: "/municipalities/sendai-city",
    fiscalSummary: "Reviewed 55項目（財政レコード4件・決算51件）",
  },
  "shizuoka-city": {
    name: "静岡市", type: "政令指定都市",
    summary: "第5次静岡市総合計画の施策10系列（KPI23件）、普通会計決算51件、難波喬司市長の公約3件と静岡市議会の会派別賛否495件を確認します。",
    status: "財政データ公開", href: "/municipalities/shizuoka-city",
    fiscalSummary: "Reviewed 55項目（財政レコード4件・決算51件）",
  },
  "hamamatsu-city": {
    name: "浜松市", type: "政令指定都市",
    summary: "浜松市総合計画第2期基本計画の基本政策10系列（KPI18件）、普通会計決算51件、中野祐介市長の公約10件と浜松市議会の議員別賛否を確認します。",
    status: "財政データ公開", href: "/municipalities/hamamatsu-city",
    fiscalSummary: "Reviewed 55項目（財政レコード4件・決算51件）",
  },
  "hiroshima-city": {
    name: "広島市", type: "政令指定都市",
    summary: "第6次広島市基本計画（2020〜2030年度）と実施計画（2025-2030）、2026年度当初予算、2022〜2024年度の普通会計決算に加え、松井 一實市長の現任期を公式出典で確認します。公約原文は未登録です。自治体別ページは準備中です。",
    status: "財政データ公開", href: null,
    fiscalSummary: "Reviewed 55項目（財政レコード4件・決算51件）",
  },
  "kyoto-city": {
    name: "京都市", type: "政令指定都市",
    summary: "京都基本構想（2026〜2050）と新京都戦略、2026年度当初予算、2022〜2024年度の普通会計決算に加え、松井 孝治市長の現任期を公式出典で確認します。公約原文は未登録です。自治体別ページは準備中です。",
    status: "財政データ公開", href: null,
    fiscalSummary: "Reviewed 55項目（財政レコード4件・決算51件）",
  },
  "niigata-city": {
    name: "新潟市", type: "政令指定都市",
    summary: "新潟市総合計画2030（2023〜2030年度）、2026年度当初予算、2022〜2024年度の普通会計決算に加え、中原 八一市長の現任期を公式出典で確認します。公約原文は未登録です。自治体別ページは準備中です。",
    status: "財政データ公開", href: null,
    fiscalSummary: "Reviewed 55項目（財政レコード4件・決算51件）",
  },
};

export const sourceCatalog = [
  ...(hokkaidoFinanceCatalog.records as SourceRecord[]),
  ...(kanagawaFinanceCatalog.records as SourceRecord[]),
  ...(saitamaFinanceCatalog.records as SourceRecord[]),
  ...(chibaFinanceCatalog.records as SourceRecord[]),
  ...(hyogoFinanceCatalog.records as SourceRecord[]),
  ...(miyagiFinanceCatalog.records as SourceRecord[]),
  ...(shizuokaFinanceCatalog.records as SourceRecord[]),
  ...(hiroshimaFinanceCatalog.records as SourceRecord[]),
  ...(kyotoCityFinanceCatalog.records as SourceRecord[]),
  ...(niigataCityFinanceCatalog.records as SourceRecord[]),
  ...(kyotoFinanceCatalog.records as SourceRecord[]),
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
