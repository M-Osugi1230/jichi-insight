import type { Metadata } from "next";

import { PageIntro } from "@/components/PageIntro";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { formatDateJa } from "@/lib/executives";
import {
  evidenceForSourceRequest,
  executiveForSourceRequest,
  municipalityForSourceRequest,
  sourceRequestChannelLabel,
  sourceRequestRecords,
  sourceRequestStatusLabel,
} from "@/lib/sourceRequests";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "公約資料の照会案",
  description:
    "公約原文資料を確認するために準備した行政機関への照会案と、送信・回答状況を公開します。",
};

export default function SourceRequestsPage() {
  const sent = sourceRequestRecords.filter((request) => request.sent_at).length;
  const answered = sourceRequestRecords.filter((request) => request.response_received_at).length;

  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <PageIntro eyebrow="Source request drafts" title="照会案を作ったことと、送信したことを分ける。">
          <p>
            公開資料を特定できなかった場合に、行政機関へ確認する文案を準備します。
            現在の2件はどちらも未送信で、行政機関への問い合わせや回答受領の事実はありません。
          </p>
        </PageIntro>

        <section className={styles.summaryGrid} aria-label="照会状況">
          <article className={styles.summaryCard}>
            <span>照会案</span><strong>{sourceRequestRecords.length}</strong><p>福岡県・福岡市の2件。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>送信済み</span><strong>{sent}</strong><p>明示承認前は送信しません。</p>
          </article>
          <article className={styles.summaryCard}>
            <span>回答受領</span><strong>{answered}</strong><p>未送信のため回答も0件。</p>
          </article>
        </section>

        <section className="contentSection">
          <p className="eyebrow">Prepared requests</p>
          <h2>確認したい資料と、送信前の文面</h2>
          <div className={styles.requestList}>
            {sourceRequestRecords.map((request) => {
              const term = executiveForSourceRequest(request);
              const municipality = municipalityForSourceRequest(request);
              const evidence = evidenceForSourceRequest(request);
              return (
                <article className={styles.requestCard} key={request.id}>
                  <div className={styles.cardHeader}>
                    <div>
                      <p>{municipality.name}・{term.office === "governor" ? "知事" : "市長"}</p>
                      <h3>{request.organization}</h3>
                    </div>
                    <StatusBadge label={sourceRequestStatusLabel(request.status)} tone="progress" />
                  </div>

                  <dl className={styles.facts}>
                    <div><dt>作成日</dt><dd>{formatDateJa(request.prepared_at)}</dd></div>
                    <div><dt>送信日時</dt><dd>{request.sent_at ?? "未送信"}</dd></div>
                    <div><dt>回答日時</dt><dd>{request.response_received_at ?? "未受領"}</dd></div>
                    <div><dt>レビュー</dt><dd>Reviewed</dd></div>
                  </dl>

                  <div className={styles.block}>
                    <p>Official contact channels</p>
                    <ul>
                      {request.contact_channels.map((channel) => (
                        <li key={`${channel.kind}-${channel.value}`}>
                          {sourceRequestChannelLabel(channel.kind)}：{channel.value}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className={styles.block}>
                    <p>確認したい資料</p>
                    <ul>{request.requested_items.map((item) => <li key={item}>{item}</li>)}</ul>
                  </div>

                  <div className={styles.draft}>
                    <p>件名</p>
                    <strong>{request.subject}</strong>
                    <p>送信前文案</p>
                    <div>{request.request_body}</div>
                  </div>

                  <div className={styles.block}>
                    <p>公開上の注意</p>
                    <ul>
                      <li>この文案は未送信です。</li>
                      <li>送信者の個人情報は公開データに含めません。</li>
                      {evidence?.open_questions.map((question) => <li key={question}>未決定：{question}</li>)}
                    </ul>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">No implied contact</p>
            <h2>照会案2件。送信済み0件。回答受領0件。</h2>
            <p>
              送信する場合は、宛先・文面・送信者情報を別途確認し、送信日時を記録してから状態を更新します。
            </p>
          </div>
        </section>
      </div>
      <SiteFooter />
    </main>
  );
}
