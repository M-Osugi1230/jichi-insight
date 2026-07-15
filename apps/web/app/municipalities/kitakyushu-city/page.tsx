import type { Metadata } from "next";
import Link from "next/link";

import { EvidencePanel } from "@/components/EvidencePanel";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { formatExactYen, formatJapaneseYen } from "@/lib/finance";
import {
  evidenceForKitakyushuRecord,
  kitakyushuBudgetRecord,
  kitakyushuSettlementRecord,
} from "@/lib/kitakyushuFinance";

import styles from "../fukuoka-prefecture/page.module.css";

export const metadata: Metadata = {
  title: "北九州市｜2026年度当初予算案と2024年度決算",
  description:
    "北九州市の2026年度一般会計当初予算案と2024年度一般会計決算を、公式資料の該当ページと確認状態付きで表示します。",
};

export default function KitakyushuCityPage() {
  const budgetRevenue = kitakyushuBudgetRecord("total_revenue");
  const budgetTax = kitakyushuBudgetRecord("local_tax");
  const settlementRevenue = kitakyushuSettlementRecord("total_revenue");
  const settlementExpenditure = kitakyushuSettlementRecord("total_expenditure");
  const settlementTax = kitakyushuSettlementRecord("local_tax");
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
            <h1>北九州市</h1>
            <p>
              現在は、2026年度一般会計の<strong>当初予算案</strong>2項目と、
              2024年度一般会計の<strong>決算</strong>3項目を公開しています。
              重点事業、市長公約、市議会の評価はまだ行っていません。
            </p>
          </div>
          <dl className={styles.heroFacts}>
            <div><dt>確認済み財政値</dt><dd>5項目</dd></div>
            <div><dt>収録年度</dt><dd>2024・2026</dd></div>
            <div><dt>最終確認</dt><dd>2026年7月15日</dd></div>
          </dl>
        </section>

        <section className={styles.scope} aria-labelledby="kitakyushu-scope-title">
          <div>
            <p className="eyebrow">Scope</p>
            <h2 id="kitakyushu-scope-title">予算案と決算を、同じ数字として扱わない。</h2>
          </div>
          <p>
            2026年度は年度開始時の計画、2024年度は年度終了後の実績です。
            年度と段階を明示し、当初予算案から決算へ直結するような比較や成果評価は行いません。
          </p>
        </section>

        <section className={styles.headline} aria-labelledby="kitakyushu-budget-title">
          <div className="sectionIntro">
            <p className="eyebrow">2026 initial budget proposal</p>
            <h2 id="kitakyushu-budget-title">2026年度一般会計の計画規模</h2>
            <p>
              北九州市の計数資料から、一般会計当初予算案と市税収入を確認しました。
              一般会計予算額は公式資料で過去最高と説明されています。
            </p>
          </div>
          <div className={styles.metricGrid}>
            <article className={styles.metricCard}>
              <span>一般会計当初予算案</span>
              <strong>{formatJapaneseYen(budgetRevenue.amount_yen)}</strong>
              <small>{formatExactYen(budgetRevenue.amount_yen)}</small>
              <p>公式表の647,684百万円を円へ換算。</p>
            </article>
            <article className={styles.metricCard}>
              <span>市税収入</span>
              <strong>{formatJapaneseYen(budgetTax.amount_yen)}</strong>
              <small>公式資料の表示精度：億円</small>
              <p>個人市民税・固定資産税などの増収を見込む。</p>
            </article>
            <article className={`${styles.metricCard} ${styles.derived}`}>
              <span>当初予算案に対する市税収入</span>
              <strong>{taxShare === null ? "評価不能" : `${taxShare.toFixed(1)}%`}</strong>
              <small>Jichi Insightによる単純計算</small>
              <p>市税収入 ÷ 一般会計当初予算案。財源構成全体の評価ではありません。</p>
            </article>
          </div>
        </section>

        <section className={styles.headline} aria-labelledby="kitakyushu-settlement-title">
          <div className="sectionIntro">
            <p className="eyebrow">2024 general-account settlement</p>
            <h2 id="kitakyushu-settlement-title">2024年度一般会計の決算</h2>
            <p>
              歳入、歳出、市税をそれぞれの公式決算表から千円単位で確認し、円へ換算しました。
            </p>
          </div>
          <div className={styles.metricGrid}>
            <article className={styles.metricCard}>
              <span>一般会計歳入決算額</span>
              <strong>{formatJapaneseYen(settlementRevenue.amount_yen)}</strong>
              <small>{formatExactYen(settlementRevenue.amount_yen)}</small>
              <p>前年度比1.6%増。</p>
            </article>
            <article className={styles.metricCard}>
              <span>一般会計歳出決算額</span>
              <strong>{formatJapaneseYen(settlementExpenditure.amount_yen)}</strong>
              <small>{formatExactYen(settlementExpenditure.amount_yen)}</small>
              <p>前年度比1.5%増。</p>
            </article>
            <article className={styles.metricCard}>
              <span>市税決算額</span>
              <strong>{formatJapaneseYen(settlementTax.amount_yen)}</strong>
              <small>{formatExactYen(settlementTax.amount_yen)}</small>
              <p>前年度比0.5%減。</p>
            </article>
            <article className={`${styles.metricCard} ${styles.derived}`}>
              <span>歳入−歳出（単純差額）</span>
              <strong>{formatJapaneseYen(formalBalance)}</strong>
              <small>{formatExactYen(formalBalance)}</small>
              <p>Jichi Insightによる差額計算。実質収支とは異なります。</p>
            </article>
          </div>
        </section>

        <section className={styles.evidence} aria-labelledby="kitakyushu-evidence-title">
          <div className="sectionIntro">
            <p className="eyebrow">Evidence trail</p>
            <h2 id="kitakyushu-evidence-title">計画と実績の5値を、公式表へ戻せる。</h2>
            <p>資料ページ、該当表、単位変換、表示精度の制約をEvidence Packetとして保持します。</p>
          </div>
          <div className={styles.evidenceGrid}>
            {[budgetRevenue, budgetTax, settlementRevenue, settlementExpenditure, settlementTax].map(
              (record) => (
                <EvidencePanel
                  key={record.id}
                  record={record}
                  packet={evidenceForKitakyushuRecord(record.id)}
                />
              ),
            )}
          </div>
        </section>

        <section className={styles.notAssessed}>
          <div><p className="eyebrow">Not assessed yet</p><h2>まだ評価していないこと</h2></div>
          <ul>
            <li>2026年度予算の執行状況</li>
            <li>目的別・性質別支出の妥当性</li>
            <li>重点事業、契約、KPI、成果の接続</li>
            <li>市長公約の進捗と外部要因</li>
            <li>市議会の審議、修正、採決、監視活動</li>
          </ul>
        </section>

        <nav className={styles.bottomNav} aria-label="関連ページ">
          <Link href="/sources#kitakyushu-city">北九州市の公式資料一覧</Link>
          <Link href="/data-quality">データ品質</Link>
          <Link href="/municipalities">自治体一覧</Link>
        </nav>
      </div>
      <SiteFooter />
    </main>
  );
}
