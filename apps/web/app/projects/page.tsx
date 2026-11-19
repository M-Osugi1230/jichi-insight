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
  const themes = [...new Set(reviewed.map((project) => project.policy_area))].sort();

  return (
    <>
      <SiteHeader />
      <main className="pageShell">
        <h1>重点事業</h1>
        <p>3自治体の Reviewed 事業レコードを掲載しています。公式母集団から各政策の柱ごとに掲載順で選定したものであり、金額順・優先度順・独自ランキングではありません。</p>
        <p>確認できること：福岡県・福岡市・北九州市の登録済み重点事業の予算・KPI・公式評価。まだ確認できないこと：3自治体のすべての事業を網羅した一覧ではありません。未収録の項目を推測で補いません。</p>

        <ProgressiveRecordFilter
          kind="projects"
          total={reviewed.length}
          themes={themes}
        >
          {areas.map(([key, area]) => (
            <section className={styles.section} key={key} data-filter-section="">
              <h2>{area.name}｜登録事業</h2>
              <p className={styles.meta}>母集団：{area.selection.population?.description ?? "詳細未収録"}</p>
              <p className={styles.meta}>選定方法：{area.selection.selection_rule?.description ?? "選定規則未収録"}</p>
              <p className={styles.meta}>選定カタログ更新：{area.selection.updated_at ?? "未収録"}。選定・除外理由は Reviewed 選定カタログで管理しています。</p>
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
