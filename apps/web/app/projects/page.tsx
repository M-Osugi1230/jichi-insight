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
};
const stageLabels: Record<string, string> = {
  initial_budget: "当初予算",
  revised_budget: "補正予算",
  execution: "執行",
  settlement: "決算",
};

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
        <p>18自治体の Reviewed 事業レコードを掲載しています。公式母集団から各政策の柱ごとに掲載順で選定したものであり、金額順・優先度順・独自ランキングではありません。</p>
        <p>確認できること：福岡県・福岡市・北九州市・愛知県・名古屋市・豊田市・北海道・札幌市・旭川市・大阪府・大阪市・堺市・神奈川県・横浜市・川崎市・埼玉県・さいたま市・川口市の登録済み重点事業の予算・KPI・公式評価（公表のあるもの）。埼玉県・さいたま市・川口市も登録対象です。埼玉県の登録単位は施策で、施策単位の金額と公式評価は県が公表していません（指標単位の判定のみ公表）。さいたま市は事業単位で、市の事業評価（A/B/C）と当初予算額・実績額を掲載します。川口市は施策単位で、KPIは登録済みですが計画初年度のため金額と公式評価は未公表です。まだ確認できないこと：18自治体の全事業を網羅した一覧ではありません。名古屋市の金額は予算案段階の予定額で成立値ではなく、愛知県のFY2026当初予算額は億円単位の概数です。北海道の金額は基本評価調書の「予算額」に基づく当初予算ベースで、決算額ではありません。北海道の総合判定は道の一次政策評価の判定です。豊田市・札幌市・旭川市の事業単位の公式評価は公表されていません。独自評価や順位付けは行いません。神奈川県の金額は評価報告書に億円単位で公表されたプロジェクト事業費（1億円未満切捨て）です。横浜市は施策群単位の登録であり、個別事業単位ではありません。横浜市・川崎市の金額と公式評価は、登録単位・計画年度に対応する公表値がないため未登録です。</p>

        <ProgressiveRecordFilter
          kind="projects"
          total={reviewed.length}
          themes={themes}
        >
          {areas.map(([key, area]) => (
            <section className={styles.section} key={key} id={key} data-filter-section="">
              <h2>{area.name}｜登録事業</h2>
              <p className={styles.meta}>母集団：{area.selection.population?.description ?? area.selection.population?.label ?? "詳細未収録"}</p>
              <p className={styles.meta}>選定方法：{(typeof area.selection.selection_rule === "string" ? area.selection.selection_rule : area.selection.selection_rule?.description) ?? "選定規則未収録"}</p>
              <p className={styles.meta}>選定カタログ更新：{area.selection.updated_at ?? "未収録"}。選定・除外理由は Reviewed 選定カタログで管理しています。</p>
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
