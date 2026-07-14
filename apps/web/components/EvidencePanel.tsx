import type { EvidencePacket, FiscalRecord } from "@/lib/finance";
import { formatExactYen, sourcesForRecord } from "@/lib/finance";

import styles from "./EvidencePanel.module.css";
import { StatusBadge } from "./StatusBadge";

type EvidencePanelProps = {
  record: FiscalRecord;
  packet: EvidencePacket | undefined;
};

export function EvidencePanel({ record, packet }: EvidencePanelProps) {
  const sources = sourcesForRecord(record);

  return (
    <article className={styles.panel}>
      <div className={styles.header}>
        <div>
          <p className="eyebrow">Evidence</p>
          <h3>{record.metric_label ?? record.metric}</h3>
        </div>
        <StatusBadge label="Reviewed" tone="verified" />
      </div>
      <dl className={styles.facts}>
        <div>
          <dt>保存値</dt>
          <dd>{formatExactYen(record.amount_yen)}</dd>
        </div>
        <div>
          <dt>予算段階</dt>
          <dd>当初予算</dd>
        </div>
        <div>
          <dt>対象年度</dt>
          <dd>{record.fiscal_year}年度</dd>
        </div>
      </dl>
      {packet?.claims.map((claim) => (
        <div className={styles.claim} key={`${packet.id}-${claim.field}`}>
          <p>{claim.statement}</p>
          <span>{claim.location_note}</span>
          {claim.review_note ? <small>{claim.review_note}</small> : null}
        </div>
      ))}
      <div className={styles.sources}>
        <p>一次資料</p>
        {sources.map((source) => (
          <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
            {source.title}
            <span aria-hidden="true"> ↗</span>
          </a>
        ))}
      </div>
      {packet?.open_questions.length ? (
        <div className={styles.questions}>
          <p>まだ分からないこと</p>
          <ul>
            {packet.open_questions.map((question) => (
              <li key={question}>{question}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </article>
  );
}
