import Link from "next/link";

import type { CorrectionHistoryEntry as CorrectionHistoryEntryData } from "@/lib/correctionsHistory";

/**
 * One recorded correction: before/after, reason, evidence, date and reviewer
 * (Issue #5). Shared by the public change-history page and the component
 * demo so the entry format cannot drift between them.
 */
export function CorrectionHistoryEntry({
  entry,
}: {
  entry: CorrectionHistoryEntryData;
}) {
  return (
    <article>
      <h3>{entry.target_label}</h3>
      <p>
        修正日: <time>{entry.corrected_at}</time> / レビュー担当: {entry.reviewer}
      </p>
      <p>
        <strong>修正前:</strong> {entry.before}
      </p>
      <p>
        <strong>修正後:</strong> {entry.after}
      </p>
      <p>
        <strong>理由:</strong> {entry.reason}
      </p>
      <p>
        <strong>影響範囲:</strong> {entry.affected}
      </p>
      <ul className="plainList">
        {entry.evidence.map((item) => (
          <li key={item.url}>
            根拠:{" "}
            <a href={item.url} target="_blank" rel="noreferrer">
              {item.title} ↗
            </a>
          </li>
        ))}
      </ul>
      {entry.target_path ? (
        <p>
          <Link href={entry.target_path}>対象ページを見る</Link>
        </p>
      ) : null}
      {entry.request_url ? (
        <p>
          <a href={entry.request_url} target="_blank" rel="noreferrer">
            訂正申請の記録 ↗
          </a>
        </p>
      ) : null}
    </article>
  );
}
