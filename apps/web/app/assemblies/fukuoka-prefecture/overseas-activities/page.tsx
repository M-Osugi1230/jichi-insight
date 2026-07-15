import type { Metadata } from "next";
import Link from "next/link";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { StatusBadge } from "@/components/StatusBadge";
import {
  evidenceForTrip,
  formatActivityDate,
  fukuokaOverseasActivities,
  overseasDisclosureSummary,
  sourcesForTrip,
} from "@/lib/assemblyOverseas";
import { sourceCatalog } from "@/lib/catalog";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "福岡県議会｜海外活動の公開状況",
  description:
    "福岡県議会の海外活動を、日程、目的、参加者、費用、報告書、政策反映の公開状態に分けて整理します。",
};

const reportLabels = {
  published: "報告書あり",
  not_published: "報告書未掲載",
  not_found: "報告書を確認できず",
  not_applicable: "報告書対象外",
  unknown: "報告書不明",
};

const costLabels = {
  available: "費用あり",
  not_published: "費用未掲載",
  not_found: "費用を確認できず",
  not_applicable: "費用対象外",
  unknown: "費用不明",
};

export default function OverseasActivitiesPage() {
  const contractSource = sourceCatalog.find(
    (source) => source.id === "fukuoka-pref-overseas-contract-faq",
  );
  const generalFaq = sourceCatalog.find(
    (source) => source.id === "fukuoka-pref-overseas-faq",
  );

  return (
    <main>
      <SiteHeader />
      <div className="pageShell">
        <section className={styles.hero}>
          <div>
            <div className={styles.heroMeta}>
              <span>福岡県議会</span>
              <StatusBadge label="Reviewed" tone="verified" />
            </div>
            <h1>海外活動の公開状況</h1>
            <p>
              海外活動の必要性だけでなく、誰が参加し、いくら使い、何を報告し、その後の政策へどう反映したかまで確認できることが重要です。
              現在は2026年の直近3活動を、公開されている事実と確認できない項目に分けて表示します。
            </p>
          </div>
          <dl className={styles.summaryGrid}>
            <div>
              <dt>収録活動</dt>
              <dd>{overseasDisclosureSummary.activities}件</dd>
            </div>
            <div>
              <dt>報告書あり</dt>
              <dd>{overseasDisclosureSummary.reportsPublished}件</dd>
            </div>
            <div>
              <dt>参加人数確認</dt>
              <dd>{overseasDisclosureSummary.participantListsAvailable}件</dd>
            </div>
            <div>
              <dt>費用確認</dt>
              <dd>{overseasDisclosureSummary.costsAvailable}件</dd>
            </div>
          </dl>
        </section>

        <section className={styles.gate} aria-labelledby="disclosure-gate-title">
          <div>
            <p className="eyebrow">Disclosure gate</p>
            <h2 id="disclosure-gate-title">「活動があった」と「説明できる」を分ける。</h2>
          </div>
          <ul>
            <li>公式一覧への掲載だけでは、費用や成果が公開されたとは扱いません。</li>
            <li>報告書の感想や今後の意向は、実際の政策反映と区別します。</li>
            <li>費用を確認できない場合、0円ではなく「確認できず」と表示します。</li>
            <li>参加者の公費・個人負担・政務活動費の区分は、訪問単位の資料で確認します。</li>
            <li>後日資料が公開された場合は、Evidence Packetと状態を更新します。</li>
          </ul>
        </section>

        <section className={styles.tripSection} aria-labelledby="activity-register-title">
          <div className="sectionIntro">
            <p className="eyebrow">2026 activity register</p>
            <h2 id="activity-register-title">活動ごとの公開状態</h2>
            <p>
              同じ「海外活動」でも、報告書や参加者情報の公開状況は異なります。公開されていない項目を推測で補いません。
            </p>
          </div>

          <div className={styles.tripList}>
            {fukuokaOverseasActivities.map((trip) => {
              const evidence = evidenceForTrip(trip.id);
              const sources = sourcesForTrip(trip);
              const electedMembers = trip.participants.filter(
                (participant) => participant.participant_type === "elected_member",
              );

              return (
                <article className={styles.tripCard} key={trip.id}>
                  <div className={styles.tripHeader}>
                    <div>
                      <h3>{trip.title}</h3>
                      <p>
                        {formatActivityDate(trip.start_date, trip.end_date)}／
                        {trip.destinations.join("、")}
                      </p>
                    </div>
                    <div className={styles.badges}>
                      <StatusBadge
                        label={reportLabels[trip.report_status]}
                        tone={trip.report_status === "published" ? "verified" : "warning"}
                      />
                      <StatusBadge
                        label={costLabels[trip.cost_status]}
                        tone={trip.cost_status === "available" ? "verified" : "warning"}
                      />
                    </div>
                  </div>

                  <dl className={styles.facts}>
                    <div>
                      <dt>目的</dt>
                      <dd>{trip.purpose}</dd>
                    </div>
                    <div>
                      <dt>参加人数</dt>
                      <dd>{trip.participant_count === null ? "確認できず" : `${trip.participant_count}人`}</dd>
                    </div>
                    <div>
                      <dt>総費用</dt>
                      <dd>{trip.total_cost_yen === null ? "確認できず" : `${trip.total_cost_yen}円`}</dd>
                    </div>
                    <div>
                      <dt>政策反映</dt>
                      <dd>{trip.policy_follow_up.length > 0 ? "意向あり・実施未確認" : "確認できず"}</dd>
                    </div>
                  </dl>

                  {electedMembers.length > 0 ? (
                    <div className={styles.detailBlock}>
                      <h4>報告書で確認できた議員</h4>
                      <ul className={styles.participantList}>
                        {electedMembers.map((participant) => (
                          <li key={`${trip.id}-${participant.name}`}>
                            <strong>{participant.name}</strong>
                            <span>{participant.role}</span>
                            <span>費用負担区分：確認できず</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : null}

                  <div className={styles.detailGrid}>
                    <div className={styles.detailBlock}>
                      <h4>報告書に記載された次の行動</h4>
                      {trip.policy_follow_up.length > 0 ? (
                        <ul>
                          {trip.policy_follow_up.map((item) => (
                            <li key={item}>{item}</li>
                          ))}
                        </ul>
                      ) : (
                        <p>公開資料から確認できません。</p>
                      )}
                    </div>
                    <div className={styles.detailBlock}>
                      <h4>まだ確認できないこと</h4>
                      <ul>
                        {evidence?.open_questions.map((question) => (
                          <li key={question}>{question}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className={styles.sourceLinks}>
                    {sources.map((source) => (
                      <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
                        {source.title} ↗
                      </a>
                    ))}
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <section className="contentSection" aria-labelledby="contract-process-title">
          <p className="eyebrow">Contract process</p>
          <h2 id="contract-process-title">契約手続きは、見直し方針と実施結果を分けて追う。</h2>
          <div className={styles.processGrid}>
            <article className={styles.processCard}>
              <span>Past practice</span>
              <h3>複数見積りによる随意契約</h3>
              <p>
                県議会事務局は、行程や通訳等の仕様が直前まで確定しにくいことを理由に、実績のある複数業者から見積りを取り随意契約してきたと説明しています。
              </p>
            </article>
            <article className={styles.processCard}>
              <span>Audit finding</span>
              <h3>予定価格設定への監査指摘</h3>
              <p>
                予算積算があるにもかかわらず低い予定価格で随意契約し、その後に増額変更契約を行ったとして、適切な予定価格が設定されていなかったとの注意が示されています。
              </p>
            </article>
            <article className={styles.processCard}>
              <span>Announced change</span>
              <h3>原則5者以上の指名競争入札へ</h3>
              <p>
                今後は実績と予算積算を基に仕様・予定価格を定め、指名委員会で原則5者以上を指名する方針が公表されています。
              </p>
            </article>
          </div>
          <p className={styles.warning}>
            これは公表された見直し方針です。各訪問で実際にどの方式が使われ、何者が応札し、契約額・変更額がいくらだったかは、個別の契約資料で確認する必要があります。
          </p>
          <div className={styles.sourceLinks}>
            {contractSource ? (
              <a href={contractSource.url} target="_blank" rel="noreferrer">
                契約手続きに関するQ&A ↗
              </a>
            ) : null}
            {generalFaq ? (
              <a href={generalFaq.url} target="_blank" rel="noreferrer">
                海外活動に関するQ&A ↗
              </a>
            ) : null}
          </div>
        </section>

        <section className="callout callout--dark">
          <div>
            <p className="eyebrow">No activity score yet</p>
            <h2>必要性の説明と、支出・成果の検証は両立できます。</h2>
            <p>
              国際交流に意義があることだけで費用の妥当性は決まらず、費用が高いことだけで活動全体が無意味とも決まりません。
              訪問単位の費用、契約、報告、政策反映が揃うまで、海外活動の総合点は出しません。
            </p>
          </div>
        </section>

        <nav className={styles.bottomNav} aria-label="関連ページ">
          <Link href="/assemblies">議会アカウンタビリティ</Link>
          <Link href="/sources#fukuoka-prefecture">福岡県議会の公式資料</Link>
          <Link href="/corrections">訂正・資料追加</Link>
        </nav>
      </div>
      <SiteFooter />
    </main>
  );
}
