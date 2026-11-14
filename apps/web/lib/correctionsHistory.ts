import correctionsHistoryJson from "../../../data/catalog/corrections_history.json";

/**
 * Public, read-only corrections change history.
 *
 * The canonical store is data/catalog/corrections_history.json. Only
 * corrections that were actually reviewed and applied are recorded here:
 * fictional or test entries must never be added (see docs/CORRECTIONS.md).
 * An empty entries list is a truthful state, not missing data.
 */
export type CorrectionEvidence = {
  title: string;
  url: string;
};

export type CorrectionHistoryEntry = {
  id: string;
  /** ISO date (YYYY-MM-DD) when the correction was published. */
  corrected_at: string;
  target_label: string;
  target_path: string | null;
  before: string;
  after: string;
  reason: string;
  evidence: CorrectionEvidence[];
  reviewer: string;
  affected: string;
  request_url: string | null;
};

type CorrectionsHistoryFile = {
  schema_version: string;
  updated_at: string;
  entries: CorrectionHistoryEntry[];
};

const file = correctionsHistoryJson as unknown as CorrectionsHistoryFile;

// A publication build must fail rather than display an inconsistent history.
const ids = new Set<string>();
for (const entry of file.entries) {
  if (ids.has(entry.id)) {
    throw new Error(`Duplicate correction history id: ${entry.id}`);
  }
  ids.add(entry.id);
  if (!entry.before || !entry.after || !entry.reason || entry.evidence.length === 0) {
    throw new Error(`Incomplete correction history entry: ${entry.id}`);
  }
}

const entries = [...file.entries].sort((a, b) =>
  b.corrected_at.localeCompare(a.corrected_at),
);

export const correctionsHistory = {
  updatedAt: file.updated_at,
  entries,
  total: entries.length,
};
