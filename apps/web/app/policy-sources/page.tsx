import type { Metadata } from "next";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  extractionTargetLabels,
  policySourceMunicipalities,
  policySourcePeriod,
  policySourceRoleLabels,
  policySourcesForMunicipality,
  policySourceStats,
} from "@/lib/policySources";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "政策資料マップ",
  description:
    "福岡県・福岡市・北九州市の総合計画、実施計画、年度施策、進捗報告、事業点検の収集状況を確認できます。",
};

const collectionFlow = [
  ["総合・基本計画", "自治体が目指す姿、目標、施策体系を確認"],
  ["実施計画", "具体的な事業、期間、優先順位、計画事業費を接続"],
  ["年度主要施策", "その年度に何へ重点配分するかを確認"],
  ["進捗・事業点検", "KPI、実績、課題、見直し内容を確認"],
  ["予算・決算・契約", "投入額、執行、支払先、成果へ接続"],
];

export default function PolicySourcesPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Policy source map" title="集められる政策資料から、先に形にする。">
          <p>
            公約や評価が揃うのを待たず、自治体がすでに公開している計画、年度施策、進捗報告、事業点検を整理します。
            ここでは資料の所在と抽出予定項目を公開し、まだ抽出していない内容を評価済みとして扱いません。
          </p>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="政策資料カタログ概要">
          <article className={styles.summaryCard}>
            <span>登録済み政策資料</span>
            <strong>{policySourceStats.total}</strong>
            <p>計画から事業点検まで、公式ページとPDFを登録。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>対象自治体</span>
            <strong>{policySourceStats.municipalities}</strong>
            <p>福岡県、福岡市、北九州市。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>直接確認できるPDF</span>
            <strong>{policySourceStats.pdfs}</strong>
            <p>目標、事業、予算、KPIを抽出できる一次資料。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>抽出準備済み</span>
            <strong>{policySourceStats.readyForExtraction}</strong>
            <p>資料登録済み。個別データはこれから人が確認して収録。</p>
          </article>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Accountability chain</p>
          <h2>計画から支出と成果まで、順番につなぐ。</h2>
          <ol className={styles.flow}>
            {collectionFlow.map(([title, description]) => (
              <li key={title}>
                <strong>{title}</strong>
                <span>{description}</span>
              </li>
            ))}
          </ol>
        </section>

        {policySourceMunicipalities.map((municipality) => {
          const sources = policySourcesForMunicipality(municipality.key);
          return (
            <section className={styles.group} id={municipality.key} key={municipality.key}>
              <div className={styles.groupHeader}>
                <div>
                  <p className="eyebrow">{municipality.type}</p>
                  <h2>{municipality.name}</h2>
                </div>
                <p>{sources.length}件を抽出候補として登録</p>
              </div>

              <div className={styles.sourceGrid}>
                {sources.map((source) => (
                  <article className={styles.sourceCard} key={source.id}>
                    <div>
                      <div className={styles.sourceHeader}>
                        <div>
                          <p>{policySourceRoleLabels[source.source_role]}</p>
                          <h3>{source.title}</h3>
                        </div>
                        <StatusBadge label="抽出準備済み" tone="progress" />
                      </div>
                      <p>{source.notes}</p>
                      <a href={source.url} target="_blank" rel="noreferrer">
                        公式資料を開く ↗
                      </a>
                    </div>

                    <dl className={styles.facts}>
                      <div>
                        <dt>期間</dt>
                        <dd>{policySourcePeriod(source)}</dd>
                      </div>
                      <div>
                        <dt>形式</dt>
                        <dd>{source.format.toUpperCase()}</dd>
                      </div>
                      <div>
                        <dt>確認状態</dt>
                        <dd>公式資料・所在確認済み</dd>
                      </div>
                      <div>
                        <dt>次に抽出する項目</dt>
                        <dd className={styles.targets}>
                          {source.extraction_targets.map((target) => (
                            <span className={styles.target} key={target}>
                              {extractionTargetLabels[target]}
                            </span>
                          ))}
                        </dd>
                      </div>
                    </dl>
                  </article>
                ))}
              </div>
            </section>
          );
        })}

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Current boundary</p>
            <h2>資料10件を登録しましたが、政策評価はまだ0件です。</h2>
            <p>
              次は、目標、施策、事業、計画事業費、KPI、実績、課題を原文位置付きで抽出します。
              資料を見つけただけの状態を、事業実績や達成度として表示しません。
            </p>
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
