import type { Metadata } from "next";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  dataQualitySnapshot,
  municipalityQuality,
  publicationGaps,
} from "@/lib/dataQuality";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "データ品質",
  description:
    "Jichi Insightの資料件数、レビュー状態、Evidence coverage、欠損、公開準備状況を確認できます。",
};

const qualityLevels = [
  ["Coverage", "対象・資料の存在を把握", "収録候補の管理"],
  ["Indexed", "公式URL、資料、年度、位置を特定", "公式資料カタログ"],
  ["Current", "後継計画・改定・有効期間を確認", "現行計画の判定"],
  ["Extracted", "候補値を抽出、未レビュー", "原則として非公開"],
  ["Reviewed", "一次資料と人が照合", "事実表示に利用"],
  ["Verified", "独立した二重確認を完了", "重要評価の主要根拠"],
  ["Published", "公開基準と画面検証を通過", "本番サイト"],
];

export default function DataQualityPage() {
  const snapshot = dataQualitySnapshot;
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Data quality" title="件数ではなく、確認の深さを公開する。">
          <p>
            資料を見つけた状態、現行資料であることを確認した状態、値を人が確認した状態、評価に使える状態は異なります。
            Jichi Insightは、収録件数と品質段階、欠損、更新日を同時に表示します。
          </p>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="データ品質概要">
          <article className={styles.summaryCard}><span>公式資料・年度別資料</span><strong>{snapshot.officialSources}</strong><p>{snapshot.pilotMunicipalities}自治体の公式入口と個別資料。</p></article>
          <article className={styles.summaryCard}><span>Reviewed財政値</span><strong>{snapshot.reviewedFiscalValues}</strong><p>当初予算{snapshot.initialBudgetValues}件、決算{snapshot.settlementValues}件。</p></article>
          <article className={styles.summaryCard}><span>Evidence coverage</span><strong>{snapshot.evidenceCoveragePercent}%</strong><p>Reviewed財政値に対応するEvidence Packetの割合。</p></article>
          <article className={styles.summaryCard}><span>公開済み評価</span><strong>{snapshot.publicEvaluations}</strong><p>比較条件と成果データが不足するため、まだ評価していません。</p></article>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Nationwide coverage readiness</p>
          <h2>全国登録、計画入口、現行性、Reviewed、公開済みを分ける。</h2>
          <div className={styles.summaryGrid} aria-label="全国展開の品質概要">
            <article className={styles.summaryCard}><span>全国登録</span><strong>{snapshot.nationwidePrefectures}</strong><p>47都道府県を共通コードと地域区分で登録。</p></article>
            <article className={styles.summaryCard}><span>公式入口確認済み</span><strong>{snapshot.verifiedPrefectureOfficialEntries}</strong><p>自治体公式ホームページを手動確認した都道府県。</p></article>
            <article className={styles.summaryCard}><span>総合計画索引済み</span><strong>{snapshot.sourceCatalogedPrefectures}</strong><p>計画資料の公式入口を固定した都道府県。</p></article>
            <article className={styles.summaryCard}><span>現行計画確認済み</span><strong>{snapshot.currentPlanConfirmedPrefectures}</strong><p>後継計画・改定・有効期間まで確認した都道府県。</p></article>
            <article className={styles.summaryCard}><span>現行性確認待ち</span><strong>{snapshot.currentPlanUnconfirmedPrefectures}</strong><p>公式計画入口はあるが、後継計画の確認が未完了。</p></article>
            <article className={styles.summaryCard}><span>Reviewed都道府県</span><strong>{snapshot.reviewedPrefectures}</strong><p>本文・数値・期間・単位を人が照合済み。</p></article>
            <article className={styles.summaryCard}><span>公開済み都道府県ページ</span><strong>{snapshot.publishedPrefecturePages}</strong><p>公開ゲートと本番確認を通過したページ。</p></article>
            <article className={styles.summaryCard}><span>公式URL候補・未確認</span><strong>{snapshot.candidatePrefectureOfficialEntries}</strong><p>全国登録済みだが、手動確認前の候補URL。</p></article>
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Policy source pipeline</p>
          <h2>公式計画を見つけた件数と、Reviewedに使える件数を分ける。</h2>
          <div className={styles.summaryGrid} aria-label="政策資料カタログと作業キュー">
            <article className={styles.summaryCard}><span>政策資料カタログ</span><strong>{snapshot.policySourceRecords}</strong><p>戦略、実施計画、年度報告、事業評価を資料単位で登録。</p></article>
            <article className={styles.summaryCard}><span>Reviewed政策資料</span><strong>{snapshot.reviewedPolicySourceRecords}</strong><p>福岡県・福岡市・北九州市で本文確認済みの資料。</p></article>
            <article className={styles.summaryCard}><span>第1波・索引済み計画</span><strong>{snapshot.indexedPolicySourceRecords}</strong><p>現行性は確認済みだが、政策本文・KPI抽出前の8都道府県。</p></article>
            <article className={styles.summaryCard}><span>北海道指標PDF</span><strong>{snapshot.indexedHokkaidoKpiSources}</strong><p>{snapshot.hokkaidoIndicatorSourcePages}ページを資料単位で索引済み。</p></article>
            <article className={styles.summaryCard}><span>Reviewed基準実装</span><strong>{snapshot.waveOnePolicyReviewReferences}</strong><p>全国展開のデータ・Evidence Packet基準として使う都道府県。</p></article>
            <article className={styles.summaryCard}><span>Reviewed化作業中</span><strong>{snapshot.waveOnePolicyActiveReviews}</strong><p>北海道は指標1〜{snapshot.reviewedHokkaidoIndicators}をReviewed化し、残る{snapshot.remainingHokkaidoIndicators}指標を抽出中。</p></article>
            <article className={styles.summaryCard}><span>作業待ち</span><strong>{snapshot.waveOnePolicyQueued}</strong><p>資料構造と作業依存関係に基づき順番に着手。</p></article>
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Policy data readiness</p>
          <h2>政策体系、数値目標、年度実績、評価を別の段階として公開する。</h2>
          <div className={styles.summaryGrid} aria-label="政策データ品質概要">
            <article className={styles.summaryCard}><span>Reviewed基本方向</span><strong>{snapshot.reviewedPolicyDirections}</strong><p>福岡県4方向と北海道3方向を原文・公式順序で登録。</p></article>
            <article className={styles.summaryCard}><span>北海道Reviewed政策分野</span><strong>{snapshot.reviewedHokkaidoPolicyFields}</strong><p>3基本方向に属する18分野を原文・公式順序で登録。</p></article>
            <article className={styles.summaryCard}><span>北海道政策体系Evidence</span><strong>{snapshot.hokkaidoPolicyEvidencePackets}</strong><p>3基本方向の名称、6分野、計画期間を一次資料と照合。</p></article>
            <article className={styles.summaryCard}><span>北海道指標位置</span><strong>{snapshot.hokkaidoIndicatorPositions}</strong><p>指標番号1〜108を公式PDFとページへ欠落なく対応。</p></article>
            <article className={styles.summaryCard}><span>北海道複数分野参照</span><strong>{snapshot.hokkaidoIndicatorRelationshipCount}</strong><p>108一意指標と113掲載行の差分を、重複KPIではなく参照として確認済み。</p></article>
            <article className={styles.summaryCard}><span>北海道Reviewed指標</span><strong>{snapshot.reviewedHokkaidoIndicators}</strong><p>指標1〜{snapshot.reviewedHokkaidoIndicators}を一次資料と照合。残り{snapshot.remainingHokkaidoIndicators}件は未Reviewed。</p></article>
            <article className={styles.summaryCard}><span>北海道KPI Evidence</span><strong>{snapshot.hokkaidoIndicatorEvidencePackets}</strong><p>Reviewed指標すべてにEvidence Packetを付与。</p></article>
            <article className={styles.summaryCard}><span>数値目標あり</span><strong>{snapshot.hokkaidoIndicatorsWithTargets}</strong><p>複数系列、減少目標、非単調な原文目標も修正せず保持。</p></article>
            <article className={styles.summaryCard}><span>目標未設定</span><strong>{snapshot.hokkaidoIndicatorsWithoutTargets}</strong><p>「―」を0へ変換せず、nullと原文説明で保持。</p></article>
            <article className={styles.summaryCard}><span>比較注意あり</span><strong>{snapshot.hokkaidoIndicatorComparabilityWarnings}</strong><p>調査対象変更、別番号、系列差などの注意を個別指標に保持。</p></article>
            <article className={styles.summaryCard}><span>北海道指標対象</span><strong>{snapshot.hokkaidoIndicatorTarget}</strong><p>重複を含む掲載行は{snapshot.hokkaidoDuplicateInclusiveIndicatorRows}。全件完了まで公開昇格しません。</p></article>
            <article className={styles.summaryCard}><span>Reviewed取組事項</span><strong>{snapshot.reviewedPolicyInitiatives}</strong><p>福岡県公式目次の1番から30番までを原文で登録。</p></article>
            <article className={styles.summaryCard}><span>Reviewed数値目標</span><strong>{snapshot.reviewedPolicyTargets}</strong><p>福岡県取組1から26の基準値・目標値118件を期間単位付きで登録。</p></article>
            <article className={styles.summaryCard}><span>年度実績へ接続済み</span><strong>{snapshot.policyTargetsActualsLinked}</strong><p>個別KPIとの年度実績対応は未実施。</p></article>
            <article className={styles.summaryCard}><span>取組進捗へ接続済み</span><strong>{snapshot.policyInitiativesProgressLinked}</strong><p>年度報告の実績・課題との対応付けは未実施。</p></article>
            <article className={styles.summaryCard}><span>政策評価済み</span><strong>{snapshot.assessedPolicyInitiatives}</strong><p>計画文と目標値だけでは成果を評価しません。</p></article>
          </div>
        </section>

        <section className="contentSection"><p className="eyebrow">Executive evidence readiness</p><h2>首長分野は、任期・探索・公約資料・分割レビュー・評価を分ける。</h2><div className={styles.summaryGrid} aria-label="首長データ品質概要">
          <article className={styles.summaryCard}><span>Reviewed現職任期</span><strong>{snapshot.reviewedExecutiveTerms}</strong><p>3自治体の現職・選挙日・任期を確認済み。</p></article>
          <article className={styles.summaryCard}><span>公約資料の探索記録</span><strong>{snapshot.manifestoSourceSearches}</strong><p>確認範囲、未発見、次の確認方法を保存。</p></article>
          <article className={styles.summaryCard}><span>安定した一次資料を未発見</span><strong>{snapshot.manifestoSourcesNotFound}</strong><p>不存在ではなく、現時点の探索結果として表示。</p></article>
          <article className={styles.summaryCard}><span>登録済み公約原文資料</span><strong>{snapshot.registeredManifestos}</strong><p>北九州市長選挙の公式選挙公報1件。</p></article>
          <article className={styles.summaryCard}><span>公約分割レビュー</span><strong>{snapshot.manifestoReviews}</strong><p>文章境界と分割可否を人手レビューした資料数。</p></article>
          <article className={styles.summaryCard}><span>個別公約レコード</span><strong>{snapshot.extractedPromiseRecords}</strong><p>明確な原文境界を確認できるまで0件を維持。</p></article>
        </div></section>

        <section className="contentSection"><p className="eyebrow">Evidence acquisition pipeline</p><h2>照会案、送信、回答を別の進捗として公開する。</h2><div className={styles.summaryGrid} aria-label="資料照会の進捗">
          <article className={styles.summaryCard}><span>照会案・送信前</span><strong>{snapshot.sourceRequestDrafts}</strong><p>文案は作成済み。行政機関へは未送信。</p></article>
          <article className={styles.summaryCard}><span>送信済み照会</span><strong>{snapshot.sourceRequestsSent}</strong><p>明示承認と送信日時の記録があるものだけを計上。</p></article>
          <article className={styles.summaryCard}><span>回答受領</span><strong>{snapshot.sourceRequestResponses}</strong><p>回答日時と回答概要を確認できるものだけを計上。</p></article>
        </div></section>

        <section className="contentSection"><p className="eyebrow">Coverage by municipality</p><h2>自治体ごとの深さを、同じ件数として扱わない。</h2><div className={styles.coverageGrid}>{municipalityQuality.map((municipality) => <article className={styles.coverageCard} key={municipality.key}><div className={styles.coverageHeader}><h3>{municipality.name}</h3><StatusBadge label={municipality.status === "reviewed-data" ? "Reviewed data" : "Indexed only"} tone={municipality.status === "reviewed-data" ? "verified" : "progress"} /></div><dl className={styles.coverageFacts}><div><dt>公式資料</dt><dd>{municipality.officialSources}件</dd></div><div><dt>Reviewed財政値</dt><dd>{municipality.reviewedFiscalValues}件</dd></div><div><dt>Evidence Packet</dt><dd>{municipality.evidencePackets}件</dd></div><div><dt>評価</dt><dd>{municipality.publicEvaluations}件</dd></div></dl></article>)}</div></section>

        <section className="contentSection"><p className="eyebrow">Quality ladder</p><h2>公開までの7段階</h2><div className={styles.qualityTableWrap}><table className={styles.qualityTable}><thead><tr><th>段階</th><th>意味</th><th>利用方法</th></tr></thead><tbody>{qualityLevels.map(([level, meaning, use]) => <tr key={level}><td>{level}</td><td>{meaning}</td><td>{use}</td></tr>)}</tbody></table></div></section>
        <section className="contentSection"><p className="eyebrow">Publication gaps</p><h2>評価を始める前に、まだ必要なもの</h2><ul className={styles.gapList}>{publicationGaps.map((gap) => <li key={gap}>{gap}</li>)}</ul></section>
        <section className="callout callout--dark"><div><p className="eyebrow">Why zero evaluations</p><h2>データ不足を、点数で埋めません。</h2><p>財政値だけでは、政策成果、首長の実行、議会の監視を公平に評価できません。類似団体比較、事業・契約・KPI、公約、議会資料が接続されるまで、評価0件を維持します。</p></div></section>
      </div>
      <SiteFooter />
    </main>
  );
}
