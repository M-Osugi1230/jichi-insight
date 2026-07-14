import type { Metadata } from "next";
import Link from "next/link";

import { EvidencePanel } from "@/components/EvidencePanel";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  evidenceForRecord,
  fiscalRecordByMetric,
  formatCompactYen,
  formatExactYen,
} from "@/lib/finance";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "福岡県｜2026年度当初予算",
  description:
    "福岡県の2026年度一般会計当初予算と県税収入を、公式資料の該当ページと確認状態付きで表示します。",
};

export default function FukuokaPrefecturePage() {
  const totalRevenue = fiscalRecordByMetric("total_revenue");
  const localTax = fiscalRecordByMetric("local_tax");
  const taxShare =
    totalRevenue.amount_yen && localTax.amount_yen
      ? (localTax.amount_yen / totalRevenue.amount_yen) * 100
      : null;

  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <section className={styles.hero}>
          <div>
            <div className={styles.heroMeta}>
              <span>都道府県</span>
              <StatusBadge label="Reviewed" tone="verified" />
            </div>
            <h1>福岡県</h1>
            <p>
              現在公開しているのは、2026年度一般会計の<strong>当初予算</strong>に関する
              2つの確認済み数値です。執行額、決算、政策成果の評価ではありません。
            </p>
          </div>
          <dl className={styles.heroFacts}>
            <div>
              <dt>対象年度</dt>
              <dd>2026年度</dd>
            </div>
            <div>
              <dt>データ段階</dt>
              <dd>当初予算</dd>
            </div>
            <div>
              <dt>最終確認</dt>
              <dd>2026年7月15日</dd>
            </div>
          </dl>
        </section>

        <section className={styles.scope} aria-labelledby="scope-title">
          <div>
            <p className="eyebrow">Scope</p>
            <h2 id="scope-title">「予算」と「実際に使った金額」を分ける。</h2>
          </div>
          <p>
            当初予算は、年度開始前に計画した金額です。年度中の補正、実際の執行額、
            年度終了後の決算とは異なります。このページだけで税金の使い方や成果の良し悪しは評価できません。
          </p>
        </section>

        <section className={styles.headline} aria-labelledby="finance-headline-title">
          <div className="sectionIntro">
            <p className="eyebrow">2026 initial budget</p>
            <h2 id="finance-headline-title">最初に確認できた財政の全体像</h2>
            <p>
              福岡県が2026年2月13日に公表した当初予算概要の同じページから、
              一般会計当初予算と県税収入を確認しました。
            </p>
          </div>
          <div className={styles.metricGrid}>
            <article className={styles.metricCard}>
              <span>一般会計当初予算</span>
              <strong>{formatCompactYen(totalRevenue.amount_yen)}</strong>
              <small>{formatExactYen(totalRevenue.amount_yen)}</small>
              <p>年度開始時点の一般会計歳入歳出規模。</p>
            </article>
            <article className={styles.metricCard}>
              <span>県税収入</span>
              <strong>{formatCompactYen(localTax.amount_yen)}</strong>
              <small>{formatExactYen(localTax.amount_yen)}</small>
              <p>県の資料では「過去最大」と記載されています。</p>
            </article>
            <article className={`${styles.metricCard} ${styles.derived}`}>
              <span>当初予算に対する県税収入</span>
              <strong>{taxShare === null ? "評価不能" : `${taxShare.toFixed(1)}%`}</strong>
              <small>Jichi Insightによる単純計算</small>
              <p>県税収入 ÷ 一般会計当初予算。財源構成全体の評価ではありません。</p>
            </article>
          </div>
        </section>

        <section className={styles.distinction} aria-labelledby="distinction-title">
          <div>
            <p className="eyebrow">Do not mix</p>
            <h2 id="distinction-title">同じ資料の5つの金額を、混同しない。</h2>
          </div>
          <div className={styles.distinctionContent}>
            <div className={styles.distinctionList}>
              <div><span>当初予算</span><strong>2兆3,000億円</strong><em>このページで表示</em></div>
              <div><span>2026年2月補正予算</span><strong>822億円</strong><em>未収録</em></div>
              <div><span>2025年12月補正予算</span><strong>310億円</strong><em>未収録</em></div>
              <div><span>2月定例会提案額</span><strong>2兆3,822億円</strong><em>未収録</em></div>
              <div><span>16か月予算</span><strong>2兆4,132億円</strong><em>説明上の合算額</em></div>
            </div>
            <p className={styles.methodNote}>
              「16か月予算」は、当初予算と前年度の補正予算を一体的に説明した金額です。
              標準的な当初予算額として置き換えず、文脈情報として分離しています。
            </p>
          </div>
        </section>

        <section className={styles.evidence} aria-labelledby="evidence-title">
          <div className="sectionIntro">
            <p className="eyebrow">Evidence trail</p>
            <h2 id="evidence-title">数字から、資料の該当ページへ戻れる。</h2>
            <p>
              保存した金額、予算段階、対象年度、資料上の場所、確認時の注意点を一つの単位で管理します。
            </p>
          </div>
          <div className={styles.evidenceGrid}>
            <EvidencePanel
              record={totalRevenue}
              packet={evidenceForRecord(totalRevenue.id)}
            />
            <EvidencePanel record={localTax} packet={evidenceForRecord(localTax.id)} />
          </div>
        </section>

        <section className={styles.notAssessed}>
          <div>
            <p className="eyebrow">Not assessed yet</p>
            <h2>まだ評価していないこと</h2>
          </div>
          <ul>
            <li>予算が実際にどこまで執行されたか</li>
            <li>事業別・契約先別に何へ支払われたか</li>
            <li>設定したKPIを達成したか</li>
            <li>住民サービスや地域経済がどう変わったか</li>
            <li>類似自治体に比べて妥当な規模か</li>
          </ul>
        </section>

        <nav className={styles.bottomNav} aria-label="関連ページ">
          <Link href="/sources#fukuoka-prefecture">福岡県の公式資料一覧</Link>
          <Link href="/methodology">評価方法</Link>
          <Link href="/municipalities">自治体一覧</Link>
        </nav>
      </div>
      <SiteFooter />
    </main>
  );
}
