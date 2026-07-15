import type { Metadata } from "next";
import Link from "next/link";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { formatExactYen, formatJapaneseYen } from "@/lib/finance";
import { cityFiscalComparison, cityTaxShares } from "@/lib/financeComparison";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "福岡市・北九州市の財政比較",
  description:
    "福岡市と北九州市の同年度・同会計・同段階の財政値だけを、比較条件と限界を明示して並べます。",
};

const stageLabels = {
  initial_budget: "当初予算案",
  settlement: "決算",
};

export default function ComparePage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <section className="pageIntro">
          <p className="eyebrow">Comparable facts only</p>
          <h1>福岡市と北九州市を、同じ条件の数字だけで見る。</h1>
          <p>
            金額の大小は、行政の良し悪しを意味しません。ここでは、政令指定都市・一般会計・同年度・同段階という条件が揃う値だけを並べます。
          </p>
        </section>

        <section className={styles.gate} aria-labelledby="comparison-gate-title">
          <div>
            <p className="eyebrow">Comparison gate</p>
            <h2 id="comparison-gate-title">比較できる範囲を先に固定する。</h2>
          </div>
          <ul>
            <li>対象は福岡市と北九州市の2政令指定都市</li>
            <li>会計区分は一般会計のみ</li>
            <li>2026年度は当初予算案、2024年度は決算として分離</li>
            <li>公式値とJichi Insightの単純計算を分離</li>
            <li>人口・行政需要・面積・産業構造を補正する前に優劣を付けない</li>
          </ul>
        </section>

        <section className="contentSection" aria-labelledby="comparison-table-title">
          <p className="eyebrow">Fiscal comparison</p>
          <h2 id="comparison-table-title">確認済みの同条件4指標</h2>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th scope="col">指標</th>
                  <th scope="col">福岡市</th>
                  <th scope="col">北九州市</th>
                </tr>
              </thead>
              <tbody>
                {cityFiscalComparison.map((metric) => (
                  <tr key={metric.id}>
                    <td>
                      <span className={styles.metricName}>{metric.label}</span>
                      <span className={styles.metricMeta}>
                        {metric.fiscalYear}年度・一般会計・{stageLabels[metric.stage]}
                      </span>
                    </td>
                    <td>
                      <span className={styles.amount}>
                        {formatJapaneseYen(metric.fukuokaAmountYen)}
                      </span>
                      <span className={styles.exact}>
                        {formatExactYen(metric.fukuokaAmountYen)}
                      </span>
                    </td>
                    <td>
                      <span className={styles.amount}>
                        {formatJapaneseYen(metric.kitakyushuAmountYen)}
                      </span>
                      <span className={styles.exact}>
                        {formatExactYen(metric.kitakyushuAmountYen)}
                      </span>
                      {metric.precisionNote ? (
                        <span className={styles.precision}>{metric.precisionNote}</span>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="tax-share-title">
          <p className="eyebrow">Derived context</p>
          <h2 id="tax-share-title">当初予算案に占める市税収入</h2>
          <div className={styles.shareGrid}>
            <article className={styles.shareCard}>
              <span>福岡市</span>
              <strong>{(cityTaxShares.fukuoka * 100).toFixed(1)}%</strong>
              <p>市税収入 ÷ 一般会計当初予算案。Jichi Insightによる単純計算。</p>
            </article>
            <article className={styles.shareCard}>
              <span>北九州市</span>
              <strong>{(cityTaxShares.kitakyushu * 100).toFixed(1)}%</strong>
              <p>市税収入 ÷ 一般会計当初予算案。市税は億円単位の公式表示を使用。</p>
            </article>
          </div>
        </section>

        <section className="contentSection" aria-labelledby="limitations-title">
          <p className="eyebrow">Not comparable yet</p>
          <h2 id="limitations-title">このページだけでは比較できないこと</h2>
          <ul className={styles.limitations}>
            <li>住民1人あたりの金額</li>
            <li>人口構成と行政需要</li>
            <li>市債残高・基金・財政健全性</li>
            <li>国・県からの財源構成</li>
            <li>事業別の費用と成果</li>
            <li>公約の達成度と議会の監視</li>
          </ul>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">No ranking yet</p>
            <h2>規模の違いを、優劣へ変換しない。</h2>
            <p>
              大きな予算は効率の悪さを意味せず、小さな予算は効率の良さを意味しません。人口・行政需要・成果が揃うまでは、順位や総合点を出しません。
            </p>
          </div>
        </section>

        <nav className={styles.links} aria-label="比較元ページ">
          <Link href="/municipalities/fukuoka-city">福岡市の根拠を見る</Link>
          <Link href="/municipalities/kitakyushu-city">北九州市の根拠を見る</Link>
          <Link href="/data-quality">データ品質を見る</Link>
        </nav>
      </div>
      <SiteFooter />
    </main>
  );
}
