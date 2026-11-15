import type { Metadata } from "next";

import { CorrectionHistoryEntry } from "@/components/CorrectionHistoryEntry";
import { EvidencePanel } from "@/components/EvidencePanel";
import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { SourceCard } from "@/components/SourceCard";
import { SourceLocation } from "@/components/SourceLocation";
import { StatusBadge } from "@/components/StatusBadge";
import {
  fictionalCorrectionEntry,
  fictionalEvidencePacket,
  fictionalFiscalRecord,
  fictionalMissingFiscalRecord,
  fictionalSourceRecords,
} from "@/lib/componentFixtures";
import { statementKindLabels } from "@/lib/statusLabels";

export const metadata: Metadata = {
  title: "コンポーネント表示デモ（架空データ）",
  description:
    "共通UIコンポーネントの表示確認用ページ。自治体名・金額・日付はすべて架空で、実在のデータではありません。",
  robots: { index: false, follow: false },
};

const dataStatusStages = [
  { label: "Coverage", tone: "neutral" },
  { label: "Indexed", tone: "progress" },
  { label: "Extracted", tone: "progress" },
  { label: "Reviewed", tone: "verified" },
  { label: "Published", tone: "verified" },
] as const;

export default function ComponentDemoPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Component demo"
          title="共通コンポーネントの表示を、架空データで確認する。"
        >
          <p>
            <strong>
              このページの自治体名・金額・日付・担当者はすべて架空です。実在の自治体のデータではありません。
            </strong>
            Issue
            #5の共通UIコンポーネント（出典カード、状態バッジ、Evidenceパネル、訂正履歴エントリ）が、欠測・未公表・評価不能を含む各状態をどう表示するかを確認するためのページです。検索エンジンには登録されません。
          </p>
        </PageIntro>

        <section className="contentSection" aria-labelledby="demo-badges-title">
          <p className="eyebrow">Status badges</p>
          <h2 id="demo-badges-title">状態は、色ではなく文字で伝える。</h2>
          <p>
            データの到達段階（Coverage / Indexed / Extracted / Reviewed /
            Published）と、文の種別（事実 / 正規化した比較 / 解釈 /
            評価）を、ラベル文字列つきのバッジで表示します。
          </p>
          <p>
            {dataStatusStages.map((stage) => (
              <StatusBadge key={stage.label} label={stage.label} tone={stage.tone} />
            ))}
          </p>
          <p>
            <StatusBadge label={statementKindLabels.fact} tone="verified" />
            <StatusBadge label={statementKindLabels.normalizedComparison} tone="progress" />
            <StatusBadge label={statementKindLabels.interpretation} tone="neutral" />
            <StatusBadge label={statementKindLabels.evaluation} tone="warning" />
          </p>
        </section>

        <section className="contentSection" aria-labelledby="demo-sources-title">
          <p className="eyebrow">Source cards</p>
          <h2 id="demo-sources-title">出典カード：状態と信頼度まで見せる。</h2>
          <p>
            左から、検証済み／抽出済み（未レビュー）／未公表・未確認の3状態です。未公表の資料には値が存在しないため、金額はどこにも0と表示されません。
          </p>
          <div className="sourceGrid">
            {fictionalSourceRecords.map((source) => (
              <SourceCard source={source} key={source.id} />
            ))}
          </div>
        </section>

        <section className="contentSection" aria-labelledby="demo-evidence-title">
          <p className="eyebrow">Evidence panels</p>
          <h2 id="demo-evidence-title">Evidenceパネル：資料位置と未確認事項。</h2>
          <p>
            主張ごとに資料位置を共通表示（資料位置ラベル）で示し、分からないことは「まだ分からないこと」として残します。架空fixtureのため、一次資料リンクは空です。2件目は値が未公表のケースで、保存値は「未確認」と表示されます。
          </p>
          <EvidencePanel record={fictionalFiscalRecord} packet={fictionalEvidencePacket} />
          <EvidencePanel record={fictionalMissingFiscalRecord} packet={undefined} />
          <SourceLocation note="予算書 第3表（架空の資料位置の単独表示例）" />
        </section>

        <section className="contentSection" aria-labelledby="demo-correction-title">
          <p className="eyebrow">Correction history entry</p>
          <h2 id="demo-correction-title">訂正履歴エントリの形式。</h2>
          <p>
            実際の変更履歴ページと同じコンポーネントで、架空の訂正1件を表示します。
          </p>
          <div className="roleGrid">
            <CorrectionHistoryEntry entry={fictionalCorrectionEntry} />
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
