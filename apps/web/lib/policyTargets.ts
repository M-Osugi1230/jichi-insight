import initiative01Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_01_target_evidence_packet.json";
import initiative01Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_01_targets.json";
import initiative02Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_02_target_evidence_packet.json";
import initiative02Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_02_targets.json";
import initiative03Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_03_target_evidence_packet.json";
import initiative03Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_03_targets.json";
import initiative04Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_04_target_evidence_packet.json";
import initiative04Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_04_targets.json";
import initiative05Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_05_target_evidence_packet.json";
import initiative05Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_05_targets.json";
import initiative06Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_06_target_evidence_packet.json";
import initiative06Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_06_targets.json";
import initiative07Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_07_target_evidence_packet.json";
import initiative07Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_07_targets.json";
import initiative08Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_08_target_evidence_packet.json";
import initiative08Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_08_targets.json";
import initiative09Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_09_target_evidence_packet.json";
import initiative09Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_09_targets.json";
import initiative10Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_10_target_evidence_packet.json";
import initiative10Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_10_targets.json";
import initiative11Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_11_target_evidence_packet.json";
import initiative11Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_11_targets.json";
import initiative12Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_12_target_evidence_packet.json";
import initiative12Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_12_targets.json";
import initiative13Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_13_target_evidence_packet.json";
import initiative13Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_13_targets.json";
import initiative14Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_14_target_evidence_packet.json";
import initiative14Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_14_targets.json";
import initiative15Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_15_target_evidence_packet.json";
import initiative15Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_15_targets.json";
import initiative16Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_16_target_evidence_packet.json";
import initiative16Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_16_targets.json";
import initiative17Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_17_target_evidence_packet.json";
import initiative17Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_17_targets.json";
import initiative18Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_18_target_evidence_packet.json";
import initiative18Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_18_targets.json";
import initiative19Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_19_target_evidence_packet.json";
import initiative19Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_19_targets.json";
import initiative20Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_20_target_evidence_packet.json";
import initiative20Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_20_targets.json";
import initiative21Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_21_target_evidence_packet.json";
import initiative21Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_21_targets.json";
import initiative22Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_22_target_evidence_packet.json";
import initiative22Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_22_targets.json";
import initiative23Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_23_target_evidence_packet.json";
import initiative23Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_23_targets.json";
import initiative24Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_24_target_evidence_packet.json";
import initiative24Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_24_targets.json";
import initiative25Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_25_target_evidence_packet.json";
import initiative25Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_25_targets.json";
import initiative26Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_26_target_evidence_packet.json";
import initiative26Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_26_targets.json";

export type PolicyTargetComponent = {
  label: string | null;
  baseline_value: number | null;
  baseline_unit: string | null;
  baseline_period: string | null;
  baseline_scope: "snapshot" | "annual" | "cumulative" | "not_available";
  target_value: number | null;
  target_unit: string | null;
  target_text?: string | null;
  target_operator?: "exact" | "at_least" | "at_most";
  target_period: string;
  target_scope:
    | "snapshot"
    | "annual"
    | "five_year_cumulative"
    | "cumulative"
    | "relative_condition";
  preferred_direction: "increase" | "decrease";
};

export type PolicyTarget = {
  id: string;
  target_number: number;
  submeasure_title_original: string;
  indicator_name_original: string;
  components: PolicyTargetComponent[];
  actual_linkage_status: "not_linked" | "partial" | "linked";
  evaluation_status: "not_assessed" | "partially_assessed" | "assessed";
};

export type PolicyTargetCatalog = {
  id: string;
  policy_initiative_id: string;
  source_ids: string[];
  source_document_url: string;
  source_page: number;
  printed_page: number;
  items: PolicyTarget[];
  reviewed_at: string;
  review_status: "reviewed" | "verified";
  confidence: "high" | "medium" | "low" | "not_assessable";
};

export type PolicyTargetEvidence = {
  id: string;
  subject_type: "policy_target_catalog";
  subject_id: string;
  claims: Array<{
    field: string;
    statement: string;
    source_ids: string[];
    location_note: string | null;
    decision: "accepted" | "rejected" | "needs_review" | "not_assessable";
    review_note: string | null;
  }>;
  open_questions: string[];
  review_status: "reviewed" | "verified";
};

export type PolicyTargetPageDefinition = {
  slug:
    | "01"
    | "02"
    | "03"
    | "04"
    | "05"
    | "06"
    | "07"
    | "08"
    | "09"
    | "10"
    | "11"
    | "12"
    | "13"
    | "14"
    | "15"
    | "16"
    | "17"
    | "18"
    | "19"
    | "20"
    | "21"
    | "22"
    | "23"
    | "24"
    | "25"
    | "26";
  title: string;
  catalog: PolicyTargetCatalog;
  evidence: PolicyTargetEvidence;
};

export const policyTargetPages: PolicyTargetPageDefinition[] = [
  {
    slug: "01",
    title: "次代を担う「人財」の育成",
    catalog: initiative01Catalog as PolicyTargetCatalog,
    evidence: initiative01Evidence as PolicyTargetEvidence,
  },
  {
    slug: "02",
    title: "世界から選ばれる福岡県の実現",
    catalog: initiative02Catalog as PolicyTargetCatalog,
    evidence: initiative02Evidence as PolicyTargetEvidence,
  },
  {
    slug: "03",
    title: "ワンヘルスの推進",
    catalog: initiative03Catalog as PolicyTargetCatalog,
    evidence: initiative03Evidence as PolicyTargetEvidence,
  },
  {
    slug: "04",
    title: "移住定住の促進",
    catalog: initiative04Catalog as PolicyTargetCatalog,
    evidence: initiative04Evidence as PolicyTargetEvidence,
  },
  {
    slug: "05",
    title: "デジタル社会の実現",
    catalog: initiative05Catalog as PolicyTargetCatalog,
    evidence: initiative05Evidence as PolicyTargetEvidence,
  },
  {
    slug: "06",
    title: "グリーン社会の実現",
    catalog: initiative06Catalog as PolicyTargetCatalog,
    evidence: initiative06Evidence as PolicyTargetEvidence,
  },
  {
    slug: "07",
    title: "成長産業の創出",
    catalog: initiative07Catalog as PolicyTargetCatalog,
    evidence: initiative07Evidence as PolicyTargetEvidence,
  },
  {
    slug: "08",
    title: "中小企業の振興",
    catalog: initiative08Catalog as PolicyTargetCatalog,
    evidence: initiative08Evidence as PolicyTargetEvidence,
  },
  {
    slug: "09",
    title: "農林水産業の振興",
    catalog: initiative09Catalog as PolicyTargetCatalog,
    evidence: initiative09Evidence as PolicyTargetEvidence,
  },
  {
    slug: "10",
    title: "地域と調和した観光産業の振興",
    catalog: initiative10Catalog as PolicyTargetCatalog,
    evidence: initiative10Evidence as PolicyTargetEvidence,
  },
  {
    slug: "11",
    title: "雇用対策の充実、魅力ある職場づくり",
    catalog: initiative11Catalog as PolicyTargetCatalog,
    evidence: initiative11Evidence as PolicyTargetEvidence,
  },
  {
    slug: "12",
    title: "健康づくり、安心で質の高い医療の提供",
    catalog: initiative12Catalog as PolicyTargetCatalog,
    evidence: initiative12Evidence as PolicyTargetEvidence,
  },
  { slug: "13", title: "スポーツ立県福岡の実現", catalog: initiative13Catalog as PolicyTargetCatalog, evidence: initiative13Evidence as PolicyTargetEvidence },
  { slug: "14", title: "文化芸術の振興", catalog: initiative14Catalog as PolicyTargetCatalog, evidence: initiative14Evidence as PolicyTargetEvidence },
  { slug: "15", title: "ジェンダー平等の社会づくり", catalog: initiative15Catalog as PolicyTargetCatalog, evidence: initiative15Evidence as PolicyTargetEvidence },
  { slug: "16", title: "高齢者、障がいのある人への支援", catalog: initiative16Catalog as PolicyTargetCatalog, evidence: initiative16Evidence as PolicyTargetEvidence },
  { slug: "17", title: "社会的・経済的に厳しい状況にある方への支援", catalog: initiative17Catalog as PolicyTargetCatalog, evidence: initiative17Evidence as PolicyTargetEvidence },
  { slug: "18", title: "人権が尊重される心豊かな社会づくり", catalog: initiative18Catalog as PolicyTargetCatalog, evidence: initiative18Evidence as PolicyTargetEvidence },
  { slug: "19", title: "外国人材に選ばれる地域づくり", catalog: initiative19Catalog as PolicyTargetCatalog, evidence: initiative19Evidence as PolicyTargetEvidence },
  { slug: "20", title: "安全で安心して暮らせる地域づくり", catalog: initiative20Catalog as PolicyTargetCatalog, evidence: initiative20Evidence as PolicyTargetEvidence },
  { slug: "21", title: "豊かな自然環境の保全と快適な生活環境の創造", catalog: initiative21Catalog as PolicyTargetCatalog, evidence: initiative21Evidence as PolicyTargetEvidence },
  { slug: "22", title: "環境に負荷をかけない社会への移行", catalog: initiative22Catalog as PolicyTargetCatalog, evidence: initiative22Evidence as PolicyTargetEvidence },
  { slug: "23", title: "防災・減災・県土強靱化", catalog: initiative23Catalog as PolicyTargetCatalog, evidence: initiative23Evidence as PolicyTargetEvidence },
  { slug: "24", title: "地域の活力向上", catalog: initiative24Catalog as PolicyTargetCatalog, evidence: initiative24Evidence as PolicyTargetEvidence },
  { slug: "25", title: "県内各地域の振興", catalog: initiative25Catalog as PolicyTargetCatalog, evidence: initiative25Evidence as PolicyTargetEvidence },
  { slug: "26", title: "生活と産業を支える基盤の整備", catalog: initiative26Catalog as PolicyTargetCatalog, evidence: initiative26Evidence as PolicyTargetEvidence },
];

export const initiative01TargetCatalog = policyTargetPages[0].catalog;
export const initiative01TargetEvidence = policyTargetPages[0].evidence;

export function policyTargetPage(slug: PolicyTargetPageDefinition["slug"]) {
  const page = policyTargetPages.find((item) => item.slug === slug);
  if (!page) {
    throw new Error(`Unknown policy target page: ${slug}`);
  }
  return page;
}

export function policyTargetStats(catalog: PolicyTargetCatalog) {
  return {
    reviewedTargets: catalog.items.length,
    actualsLinked: catalog.items.filter(
      (target) => target.actual_linkage_status !== "not_linked",
    ).length,
    assessed: catalog.items.filter(
      (target) => target.evaluation_status !== "not_assessed",
    ).length,
  };
}

export const allPolicyTargetStats = {
  reviewedTargets: policyTargetPages.reduce(
    (total, page) => total + page.catalog.items.length,
    0,
  ),
  actualsLinked: policyTargetPages.reduce(
    (total, page) => total + policyTargetStats(page.catalog).actualsLinked,
    0,
  ),
  assessed: policyTargetPages.reduce(
    (total, page) => total + policyTargetStats(page.catalog).assessed,
    0,
  ),
};

export const initiative01TargetStats = policyTargetStats(initiative01TargetCatalog);

export function formatTargetValue(
  value: number | null,
  unit: string | null,
  operator: PolicyTargetComponent["target_operator"] = "exact",
  text: string | null = null,
) {
  if (text) {
    return text;
  }
  if (value === null || unit === null) {
    return "未設定";
  }
  const suffix = operator === "at_most" ? "以下" : operator === "at_least" ? "以上" : "";
  return `${value.toLocaleString("ja-JP")}${unit}${suffix}`;
}

export function targetScopeLabel(
  scope:
    | PolicyTargetComponent["baseline_scope"]
    | PolicyTargetComponent["target_scope"],
) {
  const labels = {
    snapshot: "時点値",
    annual: "年次値",
    cumulative: "累計値",
    five_year_cumulative: "5年間累計",
    relative_condition: "条件型目標",
    not_available: "当初値なし",
  } as const;
  return labels[scope];
}
