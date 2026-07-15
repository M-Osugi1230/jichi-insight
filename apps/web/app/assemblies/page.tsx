import type { Metadata } from "next";
import Link from "next/link";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { overseasDisclosureSummary } from "@/lib/assemblyOverseas";

export const metadata: Metadata = {
  title: "議会アカウンタビリティ",
  description:
    "議会の議案、採決、費用、政務活動費、視察・海外活動を、役割と一次資料に基づいて整理します。",
};

export default function AssembliesPage() {
  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro
          eyebrow="Assembly accountability"
          title="議会を、質問数ではなく役割と根拠で見る。"
        >
          <p>
            議会の役割は、条例・予算・決算の審議、修正、監視、政策提案、住民への説明です。
            Jichi Insightは、首長の政策成果を議会の成果として直接採点せず、議会が何を決め、何を問い、何を公開したかを分けて追います。
          </p>
        </PageIntro>

        <section className="contentSection">
          <p className="eyebrow">First reviewed assembly slice</p>
          <h2>福岡県議会の海外活動</h2>
          <div className="roleGrid">
            <article>
              <div className="sectionHeadingWithBadge">
                <h3>2026年の活動台帳</h3>
                <StatusBadge label="Reviewed" tone="verified" />
              </div>
              <p>
                公式一覧に掲載された直近3件を、報告書、参加者、費用、政策反映の公開状態に分けて整理しました。
              </p>
            </article>
            <article>
              <h3>公開状態</h3>
              <p>
                報告書は{overseasDisclosureSummary.reportsPublished}/
                {overseasDisclosureSummary.activities}件、参加者人数は
                {overseasDisclosureSummary.participantListsAvailable}/
                {overseasDisclosureSummary.activities}件で確認できました。
              </p>
            </article>
            <article>
              <h3>費用</h3>
              <p>
                確認した資料では、訪問単位の総費用・1人当たり費用を確認できた活動は
                {overseasDisclosureSummary.costsAvailable}件です。費用がゼロという意味ではありません。
              </p>
            </article>
          </div>
          <div className="heroActions">
            <Link
              className="primaryAction"
              href="/assemblies/fukuoka-prefecture/overseas-activities"
            >
              海外活動台帳を見る
            </Link>
            <Link className="secondaryAction" href="/sources#fukuoka-prefecture">
              福岡県議会の公式資料を見る
            </Link>
          </div>
        </section>

        <section className="contentSection narrativeSection">
          <div>
            <p className="eyebrow">Next scope</p>
            <h2>議会全体の評価は、まだ行いません。</h2>
          </div>
          <div>
            <ul className="plainList">
              <li>議案と提出主体</li>
              <li>議員別採決の公開状況</li>
              <li>修正案・附帯決議</li>
              <li>政務活動費と成果物</li>
              <li>委員会調査と政策反映</li>
              <li>住民参加・情報公開</li>
            </ul>
            <p>
              これらを同じ期間で収集し、議会が本来担う役割ごとに比較できるまで、総合点や会派ランキングは出しません。
            </p>
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
