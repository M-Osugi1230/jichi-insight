import Link from "next/link";
import type { Metadata } from "next";

import { BreadcrumbTrail } from "@/components/BreadcrumbTrail";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  currentExecutiveTerms,
  promiseRecords,
  promisesForExecutive,
  evidenceForExecutive,
  evidenceForManifestoReview,
  evidenceForManifestoSourceSearch,
  executiveMunicipality,
  formatDateJa,
  manifestoReviewForExecutive,
  manifestoSourceSearchForExecutive,
  manifestoSourceSearchRecords,
  manifestoSourcesForExecutive,
  sourcesForExecutive,
  type ManifestoSourceSearch,
} from "@/lib/executives";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "首長台帳",
  description:
    "登録済みの知事・市長の現任期、選挙結果、公約原文資料、資料探索履歴、未評価範囲を確認できます。",
  alternates: {
    canonical: "https://jimieru.com/executives/",
  },
};

function sourceSearchStatusLabel(status: ManifestoSourceSearch["result_status"]) {
  if (status === "source_registered") {
    return "公約原文資料を登録";
  }
  if (status === "official_result_only") {
    return "公式選挙結果のみ";
  }
  if (status === "no_stable_primary_source_found") {
    return "安定した一次資料は未発見";
  }
  return "追加確認が必要";
}

export default function ExecutivesPage() {
  const electionResultsReady = currentExecutiveTerms.filter(
    (term) => sourcesForExecutive(term).some((source) => source.category === "election"),
  ).length;

  const executivesWithReviewedPromises = currentExecutiveTerms.filter((term) =>
    promisesForExecutive(term).some((promise) => promise.review_status === "reviewed"),
  );

  return (
    <>
      <SiteHeader />
      <main>
      <div className="pageShell">
        <BreadcrumbTrail items={[{name:"ホーム",href:"/"},{name:"首長台帳",href:"/executives"}]} />
        <PageIntro eyebrow="Executive registry" title="首長評価の前に、任期と公約の根拠を固定する。">
          <p>
            誰が現職か、どの選挙と任期に基づくか、公約原文をどこから取得するかを先に整理します。
            人物の好悪や政策思想は採点せず、公約・予算・事業・成果を接続できる状態をつくります。
          </p>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="首長台帳の整備状況">
          <article className={styles.summaryCard}>
            <span>現職首長</span>
            <strong>{currentExecutiveTerms.length}</strong>
            <p>任期の登録済み首長を表示。公約が未登録の首長も含みます。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>個別選挙結果</span>
            <strong>{electionResultsReady}</strong>
            <p>選挙管理委員会の個別結果ページを登録。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>公約資料の探索記録</span>
            <strong>{manifestoSourceSearchRecords.length}</strong>
            <p>見つからなかった場合も、確認範囲と次の調査を記録。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>Reviewed 公約原文</span>
            <strong>{promiseRecords.filter(p => p.review_status === "reviewed").length}</strong>
            <p>{executivesWithReviewedPromises.length}首長に Reviewed 公約を登録済み。公約未登録の首長は含めません。<Link href="/promises">公約一覧を見る</Link></p>
          </article>
          <article className={styles.summaryCard}>
            <span>公約進捗評価</span>
            <strong>0</strong>
            <p>登録した公約を一律に達成判定するものではありません。首長スコアは表示しません。</p>
          </article>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Current terms</p>
          <h2>現任期、選挙結果、公約原文資料、探索履歴を分けて見る。</h2>
          <div className={styles.registry}>
            {currentExecutiveTerms.map((term) => {
              const municipality = executiveMunicipality(term);
              const sources = sourcesForExecutive(term);
              const manifestoSources = manifestoSourcesForExecutive(term);
              const evidence = evidenceForExecutive(term);
              const manifestoReview = manifestoReviewForExecutive(term);
              const manifestoReviewEvidence = manifestoReview
                ? evidenceForManifestoReview(manifestoReview)
                : undefined;
              const sourceSearch = manifestoSourceSearchForExecutive(term);
              const sourceSearchEvidence = sourceSearch
                ? evidenceForManifestoSourceSearch(sourceSearch)
                : undefined;
              const termStartClaim = evidence?.claims.find((claim) => claim.field === "term_start");
              const vacancyElectionStart = municipality.key === "yokohama-city" &&
                Boolean(termStartClaim?.statement.includes("欠員選挙") &&
                  termStartClaim?.review_note?.includes("欠員選挙"));

              return (
                <article className={styles.executiveCard} key={term.id}>
                  <div className={styles.executiveHeader}>
                    <div>
                      <p>{municipality.name}・{term.office === "governor" ? "知事" : "市長"}</p>
                      <h3>{term.person_name}</h3>
                    </div>
                    <StatusBadge label="Reviewed" tone="verified" />
                  </div>

                  <dl className={styles.facts}>
                    <div><dt>現任期開始</dt><dd>{formatDateJa(term.term_start)}</dd></div>
                    <div><dt>任期満了</dt><dd>{formatDateJa(term.term_end)}</dd></div>
                    <div><dt>選挙日</dt><dd>{formatDateJa(term.election_date)}</dd></div>
                    {vacancyElectionStart ? (
                      <div><dt>任期起算</dt><dd>欠員選挙による選挙日起算</dd></div>
                    ) : null}
                    <div>
                      <dt>公約原文資料</dt>
                      <dd>{promisesForExecutive(term).length ? "原文公約登録済み" : "未登録"}</dd>
                    </div>
                    <div><dt>公約進捗評価</dt><dd>未実施</dd></div>
                  </dl>

                  <div className={styles.sourceList}>
                    <p>Term and election sources</p>
                    {sources.map((source) => (
                      <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
                        {source.title} ↗
                      </a>
                    ))}
                  </div>

                  {sourceSearch ? (
                    <div className={styles.gaps}>
                      <p>Manifesto source search</p>
                      <ul>
                        <li>探索日：{formatDateJa(sourceSearch.searched_at)}</li>
                        <li>結果：{sourceSearchStatusLabel(sourceSearch.result_status)}</li>
                        <li>確認範囲：{sourceSearch.search_scopes.length}区分</li>
                        <li>{sourceSearch.review_note}</li>
                        <li>未発見は、資料が存在しないという判定ではありません。</li>
                        {sourceSearch.next_actions.map((action) => (
                          <li key={action}>次の確認：{action}</li>
                        ))}
                        {sourceSearchEvidence?.open_questions.map((question) => (
                          <li key={question}>未解決：{question}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}

                  {manifestoSources.length ? (
                    <div className={styles.sourceList}>
                      <p>Manifesto source</p>
                      {manifestoSources.map((source) => (
                        <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
                          {source.title} ↗
                        </a>
                      ))}
                      <p>
                        {promisesForExecutive(term).some((promise) => promise.review_status === "reviewed")
                          ? "原文を個別公約に分割・登録済みです。達成率や首長ごとの点数は算出していません。"
                          : "公約原文は本サイトで未登録です。資料の存在や公表状況を断定するものではありません。"}
                      </p>
                    </div>
                  ) : null}

                  {manifestoReview ? (
                    <div className={styles.gaps}>
                      <p>Manifesto segmentation review</p>
                      <ul>
                        <li>状態：手動レビュー待ち</li>
                        <li>資料位置：{manifestoReview.source_location}</li>
                        <li>文章境界：政策方向・経歴・決意が混在</li>
                        <li>作成済み公約レコード：{manifestoReview.promise_records_created}件</li>
                        {manifestoReview.review_note ? <li>{manifestoReview.review_note}</li> : null}
                        {manifestoReviewEvidence?.open_questions.map((question) => (
                          <li key={question}>未解決：{question}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}

                  {evidence?.open_questions.length ? (
                    <div className={styles.gaps}>
                      <p>Open questions</p>
                      <ul>
                        {evidence.open_questions.map((question) => <li key={question}>{question}</li>)}
                      </ul>
                    </div>
                  ) : null}
                </article>
              );
            })}
          </div>
        </section>

        <section className={`contentSection ${styles.boundary}`}>
          <div>
            <p className="eyebrow">Source readiness</p>
            <h2>資料があることと、公約を評価できることは別です。未発見と不存在も、同じ意味にしません。</h2>
            <p>行政機関への公約資料の照会は、準備した文案と送信・回答の状態を分けて公開しています。<Link href="/executives/source-requests">公約資料の照会案と送信状況を見る</Link></p>
          </div>
          <ul>
            <li>個別選挙結果は登録済みの公式出典がある範囲で表示します。</li>
            <li>公約資料の探索履歴は、調査が登録された首長について表示します。</li>
            <li>Reviewed 公約原文が登録済みの首長は {executivesWithReviewedPromises.map((term) => `${executiveMunicipality(term).name}${term.office === "governor" ? "知事" : "市長"}`).join("・")}。未登録の首長を登録済みとは扱いません。</li>
            <li>福岡市長の公約は候補者HPの同時期原文引用と選挙公報見出しの照合、福岡県知事の公約は選挙公報を原典として登録</li>
            <li>資料が存在しないとは判定せず、追加確認を継続</li>
          </ul>
        </section>

        <section className={`contentSection ${styles.boundary}`}>
          <div>
            <p className="eyebrow">Evaluation boundary</p>
            <h2>現職名と任期が分かっても、実績評価はできない。</h2>
          </div>
          <ul>
            <li>登録済み公約の進捗評価に必要な公式資料の継続確認</li>
            <li>公約ごとの期限・数値目標・財源・自治体権限</li>
            <li>関連する事業、予算、契約、KPI</li>
            <li>変更・延期・中止の公式説明</li>
            <li>外部要因と首長が制御できる範囲</li>
          </ul>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Next step</p>
            <h2>登録済み公約{promiseRecords.filter((promise) => promise.review_status === "reviewed").length}件の原文と、未接続・要確認の範囲を分けて見る。</h2>
            <p>
              公約原文を登録している首長のみ掲載しています。公約が未登録の首長も首長台帳に残し、未登録と未達・未着手を混同しません。
            </p>
            <p><Link href="/promises">公約レジストリで原文・出典・関連事業を確認する</Link></p>
          </div>
        </section>
      </div>
      </main>
      <SiteFooter />
    </>
  );
}
