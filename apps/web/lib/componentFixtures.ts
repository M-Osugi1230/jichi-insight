import type { SourceRecord } from "./catalog";
import type { CorrectionHistoryEntry } from "./correctionsHistory";
import type { EvidencePacket, FiscalRecord } from "./finance";

/**
 * Fictional fixtures for the Issue #5 component demo (/component-demo).
 *
 * Every value here is invented for display testing only: the municipality,
 * amounts, dates and reviewer do not exist. URLs use example.com
 * (RFC 2606) so a fixture can never be mistaken for a real official source.
 * These fixtures must never be copied into catalogs or reviewed data.
 *
 * SourceRecord.municipality_key is an internal grouping key that SourceCard
 * does not render; the fixtures reuse an existing key value purely to
 * satisfy the type.
 */
export const fictionalSourceRecords: SourceRecord[] = [
  {
    id: "fixture-source-budget-verified",
    municipality_key: "fukuoka-city",
    organization: "架空市役所（存在しません）",
    category: "budget",
    title: "架空市 令和8年度当初予算書（架空）",
    url: "https://example.com/fictional-city/budget-2026.pdf",
    source_kind: "document",
    availability: "published",
    indexed_at: "2026-01-15",
    review_status: "verified",
    confidence: "high",
    notes: "架空の出典カードです。検証済みの状態表示を確認するために使います。",
  },
  {
    id: "fixture-source-settlement-extracted",
    municipality_key: "fukuoka-city",
    organization: "架空市役所（存在しません）",
    category: "settlement",
    title: "架空市 令和6年度決算書（架空）",
    url: "https://example.com/fictional-city/settlement-2024.pdf",
    source_kind: "document",
    availability: "published",
    indexed_at: "2026-01-15",
    review_status: "extracted",
    confidence: "medium",
    notes: "架空の出典カードです。抽出済み（未レビュー）の状態表示を確認します。",
  },
  {
    id: "fixture-source-audit-missing",
    municipality_key: "fukuoka-city",
    organization: "架空市監査委員（存在しません）",
    category: "audit",
    title: "架空市 監査結果報告書（架空）",
    url: "https://example.com/fictional-city/audit-2024.pdf",
    source_kind: "document",
    availability: "not_published",
    indexed_at: "2026-01-15",
    review_status: "missing",
    confidence: "not_assessable",
    notes: "架空の出典カードです。未公表のため値は存在せず、0とは表示しません。",
  },
];

export const fictionalFiscalRecord: FiscalRecord = {
  id: "fixture-fiscal-budget-2026",
  municipality_id: "fictional-city",
  fiscal_year: 2026,
  account_type: "general",
  stage: "initial_budget",
  metric: "general_account_initial_budget",
  metric_label: "一般会計当初予算（架空）",
  amount_yen: 123_456_000_000,
  value: null,
  unit: "円",
  value_status: "published",
  period_start: "2026-04-01",
  period_end: "2027-03-31",
  note: null,
  review_status: "reviewed",
  confidence: "high",
  sources: [],
};

export const fictionalEvidencePacket: EvidencePacket = {
  id: "fixture-packet-budget-2026",
  subject_type: "fiscal_record",
  subject_id: "fixture-fiscal-budget-2026",
  claims: [
    {
      field: "amount_yen",
      statement: "架空市の一般会計当初予算は1,234億5,600万円である（架空の主張）。",
      source_ids: [],
      location_note: "当初予算書 第1表（架空の資料位置）",
      decision: "accepted",
      review_note: "架空のレビュー記録です。実在の照合結果ではありません。",
    },
    {
      field: "fiscal_year",
      statement: "対象年度は2026年度である（架空の主張）。",
      source_ids: [],
      location_note: null,
      decision: "accepted",
      review_note: null,
    },
  ],
  open_questions: ["架空の未確認事項：特別会計との接続は確認できていません。"],
  review_status: "reviewed",
};

export const fictionalMissingFiscalRecord: FiscalRecord = {
  id: "fixture-fiscal-settlement-2024",
  municipality_id: "fictional-city",
  fiscal_year: 2024,
  account_type: "general",
  stage: "settlement",
  metric: "general_account_settlement_revenue",
  metric_label: "一般会計決算 歳入総額（架空）",
  amount_yen: null,
  value: null,
  unit: "円",
  value_status: "not_published",
  period_start: null,
  period_end: null,
  note: null,
  review_status: "missing",
  confidence: "not_assessable",
  sources: [],
};

export const fictionalCorrectionEntry: CorrectionHistoryEntry = {
  id: "correction-fixture-001",
  corrected_at: "2026-01-20",
  target_label: "架空市の予算額（架空の訂正）",
  target_path: null,
  before: "1,200億円",
  after: "1,234億5,600万円",
  reason: "架空の理由：転記ミスがあったため。",
  evidence: [
    {
      title: "架空市 当初予算書（架空資料）",
      url: "https://example.com/fictional-city/budget-2026.pdf",
    },
  ],
  reviewer: "架空のレビュー担当",
  affected: "架空の画面のみ（実在のページには影響しません）",
  request_url: null,
};
