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
        <p>12自治体の Reviewed 事業レコードを掲載しています。公式母集団から各政策の柱ごとに掲載順で選定したものであり、金額順・優先度順・独自ランキングではありません。</p>
        <p>確認できること：福岡県・福岡市・北九州市・愛知県・名古屋市・豊田市・北海道・札幌市・旭川市・大阪府・大阪市・堺市の登録済み重点事業の予算・KPI・公式評価（公表のあるもの）。まだ確認できないこと：12自治体の全事業を網羅した一覧ではありません。名古屋市の金額は予算案段階の予定額で成立値ではなく、愛知県のFY2026当初予算額は億円単位の概数です。北海道の金額は基本評価調書の「予算額」に基づく当初予算ベースで、決算額ではありません。北海道の総合判定は道の一次政策評価の判定です。豊田市・札幌市・旭川市の事業単位の公式評価は公表されていません。独自評価や順位付けは行いません。</p>

        <ProgressiveRecordFilter
          kind="projects"
          total={reviewed.length}
          themes={themes}
        >
          {areas.map(([key, area]) => (
            <section className={styles.section} key={key} id={key} data-filter-section="">
              <h2>{area.name}｜登録事業</h2>
              <p className={styles.meta}>母集団：{area.selection.population?.description ?? "詳細未収録"}</p>
              <p className={styles.meta}>選定方法：{area.selection.selection_rule?.description ?? "選定規則未収録"}</p>
              <p className={styles.meta}>選定カタログ更新：{area.selection.updated_at ?? "未収録"}。選定・除外理由は Reviewed 選定カタログで管理しています。</p>
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
