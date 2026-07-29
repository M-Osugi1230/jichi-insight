import type { Metadata } from "next";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "プライバシーポリシー",
  description: "Jichi Insightにおけるアクセス情報、訂正申請、外部サービス、個人情報の取扱方針。",
};

const updatedAt = "2026年7月29日";

export default function PrivacyPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Privacy policy" title="プライバシーポリシー">
          <p>Jichi Insightは、必要最小限の情報だけを取り扱い、公開Issueへの個人情報の投稿を求めません。</p>
          <p>最終更新：{updatedAt}</p>
        </PageIntro>

        <section className="contentSection">
          <h2>1. 取得する可能性がある情報</h2>
          <ul className="plainList">
            <li>GitHub Pages等の配信基盤が技術的に記録するIPアドレス、ユーザーエージェント、参照元、アクセス日時等</li>
            <li>訂正・反論申請で申請者が自ら入力した対象ページ、根拠資料、説明、GitHubアカウント情報等</li>
            <li>リポジトリへのIssue、Pull Request、コメントなど、利用者が公開操作によって投稿した情報</li>
          </ul>
          <p>現時点で、本サイト独自の広告トラッキング、行動プロファイリング、会員登録、決済機能は導入していません。</p>
        </section>

        <section className="contentSection">
          <h2>2. 利用目的</h2>
          <ul className="plainList">
            <li>サイトの配信、保守、障害調査および不正利用防止</li>
            <li>訂正・反論申請の受付、事実確認、回答、変更履歴の作成</li>
            <li>データ品質、表示、アクセシビリティおよび運用方法の改善</li>
          </ul>
        </section>

        <section className="contentSection">
          <h2>3. 公開Issueの注意事項</h2>
          <p>訂正申請先として利用するGitHub Issueは原則として公開されます。自宅住所、電話番号、非公開メールアドレス、家族情報、認証情報、未公表の個人情報、脆弱性情報を投稿しないでください。非公開での連絡経路が整備されるまでは、公開できない情報を送信しないでください。</p>
        </section>

        <section className="contentSection">
          <h2>4. 第三者サービス</h2>
          <p>本サイトはGitHubおよびGitHub Pagesを利用しています。外部リンク先やGitHub上での情報処理には、それぞれの提供者の規約・プライバシーポリシーが適用されます。自治体等の公式サイトへ移動した後の取扱いも、各サイトの方針に従います。</p>
        </section>

        <section className="contentSection">
          <h2>5. 保存と削除</h2>
          <p>公開Issueや変更履歴は、透明性と再現性の確保のため保存される場合があります。個人情報が誤って投稿された場合は、確認できる範囲で非表示化、編集、削除等を検討します。ただし、Gitの履歴、外部キャッシュ、通知メール等から完全に消去できない場合があります。</p>
        </section>

        <section className="contentSection">
          <h2>6. アクセス解析を導入する場合</h2>
          <p>将来アクセス解析を導入する場合は、目的、取得項目、保存期間、第三者提供、オプトアウト方法を本ページに追記し、必要な同意・告知・設定を確認したうえで導入します。</p>
        </section>

        <section className="contentSection">
          <h2>7. 方針の変更</h2>
          <p>本方針を変更した場合は最終更新日を更新します。個人情報の取扱いを実質的に拡大する変更は、可能な範囲でサイト上またはリポジトリ上に理由を記録します。</p>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
