import type { Metadata } from "next";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "訂正・反論",
  description:
    "Jichi Insightの事実訂正、根拠資料の追加、反論、変更履歴に関する公開手続。",
};

const correctionUrl =
  "https://github.com/M-Osugi1230/jichi-insight/issues/new?template=data-correction.yml";

export default function CorrectionsPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Corrections and right of reply"
          title="誤りを直せることも、透明性の一部です。"
        >
          <p>
            Jichi Insightは、誤りをゼロと断言するのではなく、誤りを見つけ、一次資料で検証し、訂正し、その履歴を残せる仕組みを公開します。
          </p>
        </PageIntro>

        <section className="contentSection">
          <p className="eyebrow">What to report</p>
          <h2>事実訂正、より強い根拠、公式な反論を受け付けます。</h2>
          <div className="roleGrid">
            <article>
              <h3>事実訂正</h3>
              <p>金額、年度、単位、会計区分、名称、日付、公約原文、採決、出典の誤り。</p>
            </article>
            <article>
              <h3>根拠の追加</h3>
              <p>より直接的な一次資料、差し替え後の公式資料、未収録の評価・監査資料。</p>
            </article>
            <article>
              <h3>反論・補足</h3>
              <p>自治体、首長、議会、議員、政党、関係機関による公式見解や説明。</p>
            </article>
          </div>
        </section>

        <section className="contentSection narrativeSection">
          <div>
            <p className="eyebrow">Required evidence</p>
            <h2>対象と根拠を具体的に記載してください。</h2>
          </div>
          <div>
            <ul className="plainList">
              <li>対象ページまたはデータ</li>
              <li>現在の記載と、正しいと考える内容</li>
              <li>公式資料URL、資料名、年度、該当ページ</li>
              <li>重大性と、誤りが与える影響</li>
            </ul>
            <p>
              根拠資料がない意見も受け付けますが、事実訂正と意見・反論は区別して扱います。
            </p>
          </div>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Process</p>
          <h2>受付から公開まで、変更履歴を残します。</h2>
          <ol className="qualitySteps">
            <li><strong>受付</strong><span>対象、根拠、個人情報の有無を確認</span></li>
            <li><strong>検証</strong><span>一次資料と既存Evidence Packetを照合</span></li>
            <li><strong>判定</strong><span>事実訂正、評価変更、反論掲載、対応なしを区別</span></li>
            <li><strong>修正</strong><span>Pull Requestと自動検証を通して反映</span></li>
            <li><strong>履歴</strong><span>修正前後、理由、根拠、日時、影響範囲を公開</span></li>
          </ol>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">Submit a correction</p>
            <h2>公開Issueには、個人情報や未公開資料を記載しないでください。</h2>
            <p>
              自宅住所、電話番号、非公開メール、家族情報、認証情報、脆弱性は公開Issueに投稿しないでください。
            </p>
          </div>
          <a className="invertedAction" href={correctionUrl} target="_blank" rel="noreferrer">
            訂正申請を開く ↗
          </a>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
