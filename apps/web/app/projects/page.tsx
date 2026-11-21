import type { Metadata } from "next";
import Link from "next/link";

import { ProgressiveRecordFilter } from "@/components/ProgressiveRecordFilter";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { projectRegistry, projectSourceCatalog, type ProjectArea } from "@/lib/projectRegistry";
import { canonicalFor } from "@/lib/pageMetadata";
import styles from "@/components/ProjectReview.module.css";

export const metadata: Metadata = {
  title: "重点事業｜公式評価と予算から成果への記録",
  alternates: { canonical: canonicalFor("/projects") },
};

// Display labels translate existing policy_area codes; they do not classify
// or infer any new project records.
const policyAreaLabels: Record<string, string> = {
  education: "教育",
  employment: "雇用",
  health: "健康",
  transport: "交通・道路",
  industry: "産業",
  welfare: "福祉",
  childcare: "子育て",
  governance: "行政運営",
  environment: "環境",
  tourism: "観光",
  housing: "住宅",
  disaster_prevention: "防災",
  digital: "デジタル",
  culture: "文化芸術",
  infrastructure: "都市・交通",
  other: "その他",
};
const stageLabels: Record<string, string> = {
  initial_budget: "当初予算",
  revised_budget: "補正予算",
  execution: "執行",
  settlement: "決算",
};

function selectionRuleDescription(value: string | { description?: string } | undefined): string {
  return typeof value === "string" ? value : value?.description ?? "選定規則未収録";
}

export default function ProjectsPage() {
  const areas = Object.entries(projectRegistry) as [ProjectArea, (typeof projectRegistry)[ProjectArea]][];
  const reviewed = areas.flatMap(([, area]) =>
    area.projects.filter((project) => project.review_status === "reviewed"),
  );
  const themes = [...new Set(reviewed.map((project) => project.policy_area))].sort().map((value) => ({
    value, label: `${policyAreaLabels[value] ?? value}（${value}）`,
  }));

  return (
    <>
      <SiteHeader />
      <main className="pageShell">
        <h1>重点事業</h1>
        <p>27自治体の Reviewed 事業レコードを掲載しています。公式母集団から各政策の柱ごとに掲載順で選定したものであり、金額順・優先度順・独自ランキングではありません。</p>
        <p>確認できること：福岡県・福岡市・北九州市・愛知県・名古屋市・豊田市・北海道・札幌市・旭川市・大阪府・大阪市・堺市・神奈川県・横浜市・川崎市・埼玉県・さいたま市・川口市・千葉県・千葉市・兵庫県・神戸市・宮城県・仙台市・静岡県・静岡市・浜松市の登録済み重点事業の予算・KPI・公式評価（公表のあるもの）。千葉県は現行総合計画の41施策から10系列を選定し、令和7年度施策評価シートの施策計（9月補正後予算額・決算額）を掲載します。施策単位の公式評定は未公表で、指標単位の進捗判定のみ公表されています。千葉市は第2次実施計画の8分野・23政策・67施策・189計画事業から政策10系列を選定しています。政策単位の予算額・公式評価・KPIは未登録で、KGI/KPIは分野単位の別登録が正本です。埼玉県・さいたま市・川口市も登録対象です。埼玉県の登録単位は施策で、施策単位の金額と公式評価は県が公表していません（指標単位の判定のみ公表）。さいたま市は事業単位で、市の事業評価（A/B/C）と当初予算額・実績額を掲載します。川口市は施策単位で、KPIは登録済みですが計画初年度のため金額と公式評価は未公表です。兵庫県は第三期「兵庫県地域創生戦略」（2025〜2029年）の3つの柱・8つの方向性の下にある取組方針66項目（再掲を除く固有64項目）から、取組方針項目10系列を選定しています。取組方針項目単位の予算額・決算額・公式評定・KPIは未公表／未登録であり、方向性単位の187指標を付け替えません。神戸市は「神戸2030ビジョン」（2026〜2030年度）の3方向性・基本政策14件から基本政策10系列を選定しています。基本政策単位の金額・公式評価・KPIは未公表／未登録であり、方向性単位のKPI21件と計画全体のWell-Being指標を付け替えません。宮城県は新・宮城の将来ビジョンの18施策から施策単位10系列を登録し、令和8年度施策評価と令和6年度施策決算を区別しています。仙台市は仙台市実施計画2024-2026の108事業から事業単位10系列を登録し、市の4段階の自己評価をそのまま表示しています。事業別当初予算額は未登録であり0円とみなしません。静岡県は総合計画「しずおか ウェルビーイングプラン」の政策の柱24件から10系列・KPI46件を登録し、指標別の評価を柱の公式総合評定に置き換えません。静岡市は第5次総合計画の101施策から施策10系列・KPI23件を登録しています。浜松市は第2期基本計画の25基本政策から基本政策10系列・KPI18件を登録しています。いずれも登録単位の金額・公式総合評定の未登録を0円や達成済みとみなしません。まだ確認できないこと：27自治体の全事業を網羅した一覧ではありません。名古屋市の金額は予算案段階の予定額で成立値ではなく、愛知県のFY2026当初予算額は億円単位の概数です。北海道の金額は基本評価調書の「予算額」に基づく当初予算ベースで、決算額ではありません。北海道の総合判定は道の一次政策評価の判定です。豊田市・札幌市・旭川市の事業単位の公式評価は公表されていません。独自評価や順位付けは行いません。神奈川県の金額は評価報告書に億円単位で公表されたプロジェクト事業費（1億円未満切捨て）です。横浜市は施策群単位の登録であり、個別事業単位ではありません。横浜市・川崎市の金額と公式評価は、登録単位・計画年度に対応する公表値がないため未登録です。</p>

        <ProgressiveRecordFilter
          kind="projects"
          total={reviewed.length}
          themes={themes}
        >
          {areas.map(([key, area]) => (
            <section className={styles.section} key={key} id={key} data-filter-section="">
              <h2>{area.name}｜登録事業</h2>
              <p className={styles.meta}>母集団：{area.selection.population?.description ?? area.selection.population?.label ?? "詳細未収録"}</p>
              <p className={styles.meta}>選定方法：{selectionRuleDescription(area.selection.selection_rule ?? area.selection.rule)}</p>
              <p className={styles.meta}>選定カタログ更新：{area.selection.updated_at ?? "未収録"}。選定・除外理由は Reviewed 選定カタログで管理しています。</p>
              {key === "saitama-prefecture" ? <p className={styles.meta}>登録単位：施策（10系列）。県の評価報告書に施策単位の予算額・決算額と公式評価は掲載されていません。金額は未登録です。県が公表するのは指標単位の判定のみであり、施策単位の公式評価を推測しません。</p> : null}
              {key === "saitama-city" ? <p className={styles.meta}>登録単位：事業（10系列）。さいたま市の事業評価 A/B/C を公式評価として、当初予算額と実績額を分けて表示します。施策単位の評価とは混同しません。</p> : null}
              {key === "kawaguchi-city" ? <p className={styles.meta}>登録単位：施策（10系列）。第6次川口市総合計画は計画初年度のため、KPIを掲載し、施策単位の金額と公式評価は未公表（未登録）です。</p> : null}
              {key === "shizuoka-prefecture" ? <p className={styles.meta}>登録単位：政策の柱（10系列、KPI46件）。静岡県総合計画「しずおか ウェルビーイングプラン」（2025〜2028年度）の政策8本・政策の柱24本から選定。成果指標のA〜D判定は指標単位で、政策の柱単位の公式総合評定ではありません。柱別の金額は未公表・未登録です。</p> : null}
              {key === "shizuoka-city" ? <p className={styles.meta}>登録単位：施策（10系列、KPI23件）。第5次静岡市総合計画（基本構想2026〜2035年度）の9分野・45政策・101施策から選定。取組単位に公表される5年間の投資的経費を合算して施策単位の当初予算額にせず、施策の公式評価も初年度のため未登録です。</p> : null}
              {key === "hamamatsu-city" ? <p className={styles.meta}>登録単位：基本政策（10系列、KPI18件）。浜松市総合計画第2期基本計画（2025〜2034年度）の7分野・25基本政策・125政策から選定。基本政策の文章評価を独自の評点に換算しません。基本政策単位の金額・評定区分は未公表・未登録です。</p> : null}
              {key === "miyagi-prefecture" ? <p className={styles.meta}>登録単位：施策（10系列）。「新・宮城の将来ビジョン」の8政策・18施策から選定。令和8年度施策評価（令和7年度事業）に基づく公式評定・目標指標と、令和7年度政策評価で示された令和6年度事業の施策決算額を区別します。令和7年度事業の施策決算合計は公表されていないため、主要事業の額を合算して補いません。</p> : null}
              {key === "sendai-city" ? <p className={styles.meta}>登録単位：事業（10系列）。仙台市基本計画2021-2030・実施計画2024-2026の8チャレンジプロジェクト＋市政運営、108事業から選定。市の自己評価（◎・○・△・×）を公式評価として表示しますが、Jichi Insightの独自評価ではありません。事業単位の当初予算額は未登録で、0円とは扱いません。</p> : null}
              {key === "hyogo-prefecture" ? <p className={styles.meta}>登録単位：取組方針項目（10系列）。第三期「兵庫県地域創生戦略」（2025〜2029年）の3つの柱・8つの方向性、取組方針66項目（再掲2項目、固有64項目）から掲載順に選定しています。取組方針項目単位の予算額・決算額・公式評定・KPIは未公表・未登録です。県の187指標は方向性単位の指標であり、取組方針項目固有のKPIには付け替えません。金額未登録は0円を意味しません。</p> : null}
              {key === "kobe-city" ? <p className={styles.meta}>登録単位：基本政策（10系列）。第6次神戸市基本計画の実施計画「神戸2030ビジョン」（2026〜2030年度）は3方向性・基本政策14件・主な施策80件（再掲を除く62件）から構成されます。基本政策単位の予算額・公式評価・KPIは未公表・未登録です。方向性単位のKPI21件と計画全体のWell-Being指標は基本政策の実績・KPIとして付け替えません。</p> : null}
              {key === "chiba-prefecture" ? <p className={styles.meta}>登録単位：施策（10系列）。現行「千葉県総合計画 ～千葉の未来をともに創る～」の41施策から選定しています。令和7年度の施策評価シートに掲載された施策計の予算額（9月補正後・当初予算ではありません）と決算額を表示します。県は施策単位の公式評定を公表しておらず、指標単位の進捗判定のみ公表しています。指標の進捗を施策評定として表示しません。</p> : null}
              {key === "chiba-city" ? <p className={styles.meta}>登録単位：政策（10系列）。千葉市基本計画第2次実施計画の8分野・23政策・67施策・計画事業189事業から選定しています。政策単位の予算額・公式評価は未登録（未公表）です。KGI/KPIは分野単位の指標として別登録されており、政策の指標として付け替えていません。</p> : null}
              {key === "kanagawa-prefecture" ? <p className={styles.meta}>金額は評価報告書「プロジェクト事業費」の億円単位の公表値（1億円未満切捨て）を円換算したものです。千円単位の内訳・プロジェクト単位の決算額・執行額は公表されていません。</p> : null}
              {key === "yokohama-city" ? <p className={styles.meta}>登録単位：施策群。横浜市中期計画の33施策群から選定した10件であり、個別事業ではありません。施策群単位の金額・公式評価は公表されていないため、金額は未登録です。施策群単位の公式評価も未公表です。</p> : null}
              {key === "kawasaki-city" ? <p className={styles.meta}>第4期実施計画の事務事業から選定した10件です。第4期実施計画に対応する事業別当初予算額は公表されていないため、金額は未登録です。第4期の公式評価は未登録（未公表）です。</p> : null}
              {key === "nagoya-city" ? <p className={styles.meta}>金額は予算案段階の「予定額」であり、成立後の事業別予算額ではありません。</p> : null}
              {key === "aichi-prefecture" ? <p className={styles.meta}>FY2026 当初予算額は、億円単位で公表された概数です。公式評価の A〜E は愛知県の判定をそのまま表示します。</p> : null}
              {key === "toyota-city" ? <p className={styles.meta}>事業単位の公式評価は公表されていません。目標・施策単位の叙述を事業評価として扱いません。</p> : null}
              {key === "hokkaido-prefecture" ? <p className={styles.meta}>基本評価調書の「予算額」に基づく当初予算ベースの施策単位合計額であり、決算額・個別事務事業の額ではありません。公式評価（総合判定）は北海道の一次政策評価の判定で、当サイトの独自評価ではありません。</p> : null}
              {key === "sapporo-city" || key === "asahikawa-city" ? <p className={styles.meta}>事業単位の公式評価は公表されていません。計画・施策単位の進捗を事業単位の評価に読み替えず、独自の評価・順位付けをしません。</p> : null}
              <div className={styles.cards}>
                {area.projects.filter((project) => project.review_status === "reviewed").map((project) => {
                  const matchedSources = project.sources
                    .map((sourceId) => projectSourceCatalog.find((source) => source.id === sourceId))
                    .filter((source): source is NonNullable<typeof source> => Boolean(source));
                  const primarySource = matchedSources.find((source) => source.url);
                  const evidencePacket = area.evidencePackets.find((packet) => packet.subject_id === project.id);
                  const budgetDisclosure = project.budget_records
                    .map((record) => record.note)
                    .filter((note): note is string => Boolean(note));
                  const evaluationDisclosure = evidencePacket?.claims
                    .filter((claim) => claim.field === "official_evaluation")
                    .map((claim) => claim.statement) ?? [];
                  const stages = [...new Set(project.budget_records.map((record) =>
                    `${record.fiscal_year}年度 ${stageLabels[record.kind] ?? record.kind}`,
                  ))];
                  const theme = policyAreaLabels[project.policy_area] ?? project.policy_area;
                  return (
                    <article
                      className={styles.card}
                      key={project.id}
                      data-filter-entry=""
                      data-filter-group={project.policy_area}
                      data-search-text={`${project.official_title} ${project.plain_title} ${project.policy_area} ${theme}`}
                    >
                      <p className={styles.meta}>{project.fiscal_year}年度 / {project.policy_area}（{theme}）</p>
                      <h3>{project.official_title}</h3>
                      <p>{project.plain_title}</p>
                      <p className={styles.meta}>段階：{stages.length ? stages.join("／") : "該当する予算・決算段階の登録なし"}</p>
                      {key === "yokohama-city" ? <p className={styles.meta}>登録単位：施策群</p> : null}
                      {budgetDisclosure.length || evaluationDisclosure.length ? (
                        <details>
                          <summary>金額・公式評価の公表状況と欠損理由</summary>
                          {budgetDisclosure.map((note, index) => <p className={styles.meta} key={`budget-note-${index}`}>金額：{note}</p>)}
                          {evaluationDisclosure.map((note, index) => <p className={styles.meta} key={`evaluation-note-${index}`}>公式評価：{note}</p>)}
                        </details>
                      ) : null}
                      {key === "saitama-city" ? <>
                        <p className={styles.meta}>さいたま市の公式事業評価（A/B/C）：{project.official_evaluation?.rating ?? "未公表"}</p>
                        <ul className={styles.meta}>{project.budget_records.map((record, index) => (
                          <li key={index}>{record.fiscal_year}年度・{record.kind === "initial_budget" ? "当初予算額" : record.kind === "settlement" ? "実績額" : stageLabels[record.kind] ?? record.kind}：{record.amount_yen === null ? "未公表" : `${record.amount_yen.toLocaleString("ja-JP")}円`}</li>
                        ))}</ul>
                      </> : null}
                      {key === "shizuoka-prefecture" ? <p className={styles.meta}>政策の柱の金額・公式総合評定は未登録。KPIのA〜D判定は成果指標単位のみです。</p> : null}
                      {key === "shizuoka-city" ? <p className={styles.meta}>施策単位の金額・公式評価は未登録。取組単位の5年合計額は転用しません。</p> : null}
                      {key === "hamamatsu-city" ? <p className={styles.meta}>基本政策単位の予算額・段階別評定は未登録。文章評価を独自スコアにしません。</p> : null}
                      {key === "miyagi-prefecture" ? <p className={styles.meta}>施策単位の公式評価・目標指標を表示。令和6年度の施策決算額と令和7年度の公表欠損を区別し、金額の推計をしません。</p> : null}
                      {key === "sendai-city" ? <p className={styles.meta}>事業単位の仙台市自己評価（◎○△×）を表示。事業ごとの予算額は未登録であり、0円とはみなしません。</p> : null}
                      {key === "hyogo-prefecture" ? <p className={styles.meta}>取組方針項目単位の金額・公式評定・KPIは未公表・未登録（0円ではありません）。方向性の187指標を取組方針項目の評価に転用しません。</p> : null}
                      {key === "kobe-city" ? <p className={styles.meta}>基本政策単位の金額・公式評価・KPIは未公表・未登録。方向性KPI21件や計画全体のWell-Being指標を基本政策へ転用しません。</p> : null}
                      {key === "chiba-prefecture" ? <p className={styles.meta}>令和7年度・施策計：9月補正後予算額と決算額を掲載。official_evaluation は未登録（県は施策単位の評定を公表していません）。</p> : null}
                      {key === "chiba-city" ? <p className={styles.meta}>政策単位の予算額・公式評価・KPIは未登録（未公表）。分野単位のKGI/KPIは別の登録単位です。</p> : null}
                      {key === "saitama-prefecture" ? <p className={styles.meta}>施策単位の金額：未公表。施策単位の公式評価：未公表（指標単位の判定のみ）。</p> : null}
                      {key === "kawaguchi-city" ? <p className={styles.meta}>KPIは登録済み。金額・公式評価：計画初年度につき未公表。</p> : null}
                      {key === "nagoya-city" ? <p className={styles.meta}>予算案段階の予定額（成立値ではありません）</p> : null}
                      {key === "aichi-prefecture" ? <p className={styles.meta}>FY2026 当初予算は億円単位の概数です。県の公式評価：{project.official_evaluation?.rating ?? "未収録"}</p> : null}
                      {key === "toyota-city" ? <p className={styles.meta}>事業単位の公式評価は公表されていません。</p> : null}
                      {key === "hokkaido-prefecture" ? <p className={styles.meta}>基本評価調書の「予算額」＝当初予算ベース（決算額ではありません）。道の一次政策評価・総合判定：{project.official_evaluation?.rating ?? "未収録"}（道の公式評価・独自評価ではありません）。</p> : null}
                      {key === "sapporo-city" || key === "asahikawa-city" ? <p className={styles.meta}>事業単位の公式評価は公表されていません。</p> : null}
                      <p className={styles.meta}>
                        出典：{primarySource ? (
                          <a href={primarySource.url} target="_blank" rel="noopener noreferrer">
                            {primarySource.title}
                          </a>
                        ) : "出典リンク未収録"}
                        {matchedSources.length > 1 ? `（他${matchedSources.length - 1}件の出典は詳細ページを参照）` : ""}
                        ／索引更新：{primarySource?.indexed_at ?? "未収録"}
                      </p>
                      <Link href={`/projects/${key}/${encodeURIComponent(project.series_id)}`}>予算・KPI・公式評価を見る</Link>
                    </article>
                  );
                })}
              </div>
            </section>
          ))}
        </ProgressiveRecordFilter>
      </main>
      <SiteFooter />
    </>
  );
}
