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
    | "12";
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
