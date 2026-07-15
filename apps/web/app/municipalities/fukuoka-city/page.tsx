import type { Metadata } from "next";
import Link from "next/link";

import { EvidencePanel } from "@/components/EvidencePanel";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  formatExactYen,
  formatJapaneseYen,
} from "@/lib/finance";
import {
  cityBudgetRecord,
  citySettlementRecord,
  evidenceForCityRecord,
} from "@/lib/fukuokaCityFinance";

import styles from "../fukuoka-prefecture/page.module.css";

export const metadata: Metadata = {
  title: "福岡市｜2026年度当初予算案と2024年度決算",
  description:
    "福岡市の2026年度一般会計当初予算案と2024年度一般会計決算を、公式資料の該当箇所と確認状態付きで表示します。",
};

export default function FukuokaCityPage() {
  const budgetRevenue = cityBudgetRecord("total_revenue");
  const budgetTax = cityBudgetRecord("local_tax");
  const settlementRevenue = citySettlementRecord("total_revenue");
  const settlementExpenditure = citySettlementRecord("total_expenditure");
  const taxShare =
    budgetRevenue.amount_yen && budgetTax.amount_yen
      ? (budgetTax.amount_yen / budgetRevenue.amount_yen) * 100
      : null;
  const formalBalance =
    settlementRevenue.amount_yen !== null && settlementExpenditure.amount_yen !== null
      ? settlementRevenue.amount_yen - settlementExpenditure.amount_yen
      : null;

  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <section className={styles.hero}>
          <div>
            <div className={styles.heroMeta}>
              <span>政令指定都市</span>
              <StatusBadge label="Reviewed" tone="verified" />
            </div>
            <h1>福岡市</h1>
            <p>
              現在は、2026年度一般会計の<strong>当初予算案</strong>2項目と、
              2024年度一般会計の<strong>決算</strong>2項目を公開しています。
              事業成果、市長公約、市議会の評価はまだ行っていません。
            </p>
          </div>
          <dl className={styles.heroFacts}>
            <div><dt>確認済み財政値</dt><dd>4項目</dd></div>
            <div><dt>収録年度</dt><dd>2024・2026</dd></div>
            <div><dt>最終確認</dt><dd>2026年7月15日</dd></div>
          </dl>
        </section>

        <section className={styles.scope} aria-labelledby="city-scope-title">
          <div>
            <p className="eyebrow">Scope</p>
            <h2 id="city-scope-title">予算案と決算を、別の事実として見る。</h2>
          </div>
          <p>
            2026年度の数値は年度開始時に示された当初予算案です。2024年度の数値は年度終了後の決算です。
            年度も段階も異なるため、増減率として直接比較せず、それぞれの意味と根拠を分けて表示します。
          </p>
        </section>

        <section className={styles.headline} aria-labelledby="city-budget-title">
          <div className="sectionIntro">
            <p className="eyebrow">2026 initial budget proposal</p>
            <h2 id="city-budget-title">2026年度に計画した一般会計の規模</h2>
            <p>
              福岡市が2026年2月20日に公表した当初予算案ページから、一般会計の規模と市税収入を確認しました。
            </p>
          </div>
          <div className={styles.metricGrid}>
            <article className={styles.metricCard}>
              <span>一般会計当初予算案</span>
              <strong>{formatJapaneseYen(budgetRevenue.amount_yen)}</strong>
              <small>{formatExactYen(budgetRevenue.amount_yen)}</small>
              <p>前年度比1.7%増。公式ページでは過去最大と説明。</p>
            </article>
            <article className={styles.metricCard}>
              <span>市税収入</span>
              <strong>{formatJapaneseYen(budgetTax.amount_yen)}</strong>
              <small>{formatExactYen(budgetTax.amount_yen)}</small>
              <p>固定資産税・都市計画税の増などにより過去最高と説明。</p>
            </article>
            <article className={`${styles.metricCard} ${styles.derived}`}>
              <span>当初予算案に対する市税収入</span>
              <strong>{taxShare === null ? "評価不能" : `${taxShare.toFixed(1)}%`}</strong>
              <small>Jichi Insightによる単純計算</small>
              <p>市税収入 ÷ 一般会計当初予算案。財源構成全体の評価ではありません。</p>
            </article>
          </div>
        </section>

        <section className={styles.headline} aria-labelledby="city-settlement-title">
          <div className="sectionIntro">
            <p className="eyebrow">2024 general-account settlement</p>
            <h2 id="city-settlement-title">2024年度に実際に計上された一般会計決算</h2>
            <p>
              福岡市の「財政のあらまし」掲載表から、千円単位の歳入・歳出決算額を円へ換算しました。
              資料注記では2025年9月中旬時点の決算見込みです。
            </p>
          </div>
          <div className={styles.metricGrid}>
            <article className={styles.metricCard}>
              <span>一般会計歳入決算額</span>
              <strong>{formatJapaneseYen(settlementRevenue.amount_yen)}</strong>
              <small>{formatExactYen(settlementRevenue.amount_yen)}</small>
              <p>公式PDFの千円単位表から換算。</p>
            </article>
            <article className={styles.metricCard}>
              <span>一般会計歳出決算額</span>
              <strong>{formatJapaneseYen(settlementExpenditure.amount_yen)}</strong>
              <small>{formatExactYen(settlementExpenditure.amount_yen)}</small>
              <p>公式PDFの千円単位表から換算。</p>
            </article>
            <article className={`${styles.metricCard} ${styles.derived}`}>
              <span>歳入−歳出（形式収支）</span>
              <strong>{formatJapaneseYen(formalBalance)}</strong>
              <small>{formatExactYen(formalBalance)}</small>
              <p>Jichi Insightによる差額計算。実質収支とは異なります。</p>
            </article>
          </div>
        </section>

        <section className={styles.evidence} aria-labelledby="city-evidence-title">
          <div className="sectionIntro">
            <p className="eyebrow">Evidence trail</p>
            <h2 id="city-evidence-title">4つの数値すべてに、戻れる根拠を付ける。</h2>
            <p>
              公式ページの該当節、PDFのページ、単位変換、資料上の注意事項をEvidence Packetとして保持しています。
            </p>
          </div>
          <div className={styles.evidenceGrid}>
            {[budgetRevenue, budgetTax, settlementRevenue, settlementExpenditure].map(
              (record) => (
                <EvidencePanel
                  key={record.id}
                  record={record}
                  packet={evidenceForCityRecord(record.id)}
                />
              ),
            )}
          </div>
        </section>

        <section className={styles.notAssessed}>
          <div>
            <p className="eyebrow">Not assessed yet</p>
            <h2>まだ評価していないこと</h2>
          </div>
          <ul>
            <li>2026年度予算が実際にどこまで執行されたか</li>
            <li>目的別・性質別に何へ支出したか</li>
            <li>主要事業と契約先、KPI、成果の対応</li>
            <li>市長公約の進捗と市の権限・外部要因</li>
            <li>市議会の審議、修正、採決、監視活動</li>
          </ul>
        </section>

        <nav className={styles.bottomNav} aria-label="関連ページ">
          <Link href="/sources#fukuoka-city">福岡市の公式資料一覧</Link>
          <Link href="/data-quality">データ品質</Link>
          <Link href="/municipalities">自治体一覧</Link>
        </nav>
      </div>
      <SiteFooter />
    </main>
  );
}
