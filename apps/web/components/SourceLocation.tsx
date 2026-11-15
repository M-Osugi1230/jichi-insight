import styles from "./SourceLocation.module.css";

/**
 * The one shared presentation for "where in the source document" (Issue #5).
 * EvidencePanel claims and the Phase 15 source catalog used to render the
 * location note differently (a bare span vs. an ad-hoc paragraph); both now
 * go through this component so the label and wording stay identical.
 */
export function SourceLocation({ note }: { note: string }) {
  return (
    <div className={styles.location}>
      <span className={styles.label}>資料位置</span>
      <span>{note}</span>
    </div>
  );
}
