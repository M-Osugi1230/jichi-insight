import type { Metadata } from "next";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  currentExecutiveTerms,
  evidenceForExecutive,
  executiveMunicipality,
  formatDateJa,
  sourcesForExecutive,
} from "@/lib/executives";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "首長台帳",
  description:
    "福岡県知事、福岡市長、北九州市長の現任期、選挙日、公式情報、公約資料の整備状況を確認できます。",
};

export default function ExecutivesPage() {
  const manifestoReady = currentExecutiveTerms.filter(
    (term) => term.manifesto_source_ids.length > 0,
  ).length;

  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
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
            <p>福岡県知事、福岡市長、北九州市長。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>Evidence Packet</span>
            <strong>{currentExecutiveTerms.filter((term) => evidenceForExecutive(term)).length}</strong>
            <p>現職名、選挙日、未解決事項を記録。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>公約原文の登録</span>
            <strong>{manifestoReady}</strong>
            <p>安定した一次資料の登録前は進捗評価を始めません。</p>
          </article>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Current terms</p>
          <h2>現任期と、確認できていない範囲</h2>
          <div className={styles.registry}>
            {currentExecutiveTerms.map((term) => {
              const municipality = executiveMunicipality(term);
              const sources = sourcesForExecutive(term);
              const evidence = evidenceForExecutive(term);
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
                    <div><dt>選挙日</dt><dd>{formatDateJa(term.election_date)}</dd></div>
                    <div><dt>公約原文</dt><dd>{term.manifesto_source_ids.length ? "登録済み" : "未登録"}</dd></div>
                    <div><dt>評価</dt><dd>未実施</dd></div>
                  </dl>

                  <div className={styles.sourceList}>
                    <p>Official sources</p>
                    {sources.map((source) => (
                      <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
                        {source.title} ↗
                      </a>
                    ))}
                  </div>

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
            <p className="eyebrow">Evaluation boundary</p>
            <h2>現職名と任期が分かっても、実績評価はできない。</h2>
          </div>
          <ul>
            <li>公約原文の完全な収録</li>
            <li>公約ごとの期限・数値目標・財源・自治体権限</li>
            <li>関連する事業、予算、契約、KPI</li>
            <li>変更・延期・中止の公式説明</li>
            <li>外部要因と首長が制御できる範囲</li>
          </ul>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Next step</p>
            <h2>公約を一文ずつ台帳化し、事業と成果へ接続する。</h2>
            <p>
              次の工程では、選挙公報や本人公表資料の原文を保存し、要約、期限、目標、財源、自治体の権限、関連事業を分けて記録します。
            </p>
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
