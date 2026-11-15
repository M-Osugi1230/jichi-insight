import type { SourceRecord } from "@/lib/catalog";
import {
  sourceAvailabilityPresentation,
  sourceConfidenceLabel,
  sourceReviewStatusPresentation,
} from "@/lib/statusLabels";

import { StatusBadge } from "./StatusBadge";

const categoryLabels: Record<string, string> = {
  official_profile: "公式サイト",
  comprehensive_plan: "計画",
  project_evaluation: "事業評価",
  audit: "監査",
  budget: "予算",
  settlement: "決算",
  budget_settlement: "予算・決算",
  contracts: "契約",
  procurement: "入札・契約",
  election: "選挙",
  election_audit: "選挙・監査",
  executive: "首長",
  assembly: "議会",
  political_activity_expenses: "政務活動費",
  proposals: "政策提案",
  inspection_trips: "視察・海外活動",
  priority_projects: "重点事業",
  plans_election: "計画・選挙",
  disclosure_statistics_audit: "公開・統計・監査",
};

export function SourceCard({ source }: { source: SourceRecord }) {
  const reviewStatus = sourceReviewStatusPresentation(source.review_status);
  const availability = sourceAvailabilityPresentation(source.availability);
  return (
    <article className="sourceCard">
      <div className="sourceCardMeta">
        <span>{categoryLabels[source.category] ?? source.category}</span>
        <span>確認日 {source.indexed_at}</span>
      </div>
      <h3>{source.title}</h3>
      <p>{source.notes}</p>
      <div className="sourceCardStatus">
        <StatusBadge label={reviewStatus.label} tone={reviewStatus.tone} />
        <StatusBadge label={availability.label} tone={availability.tone} />
        <span className="sourceCardConfidence">
          {sourceConfidenceLabel(source.confidence)}
        </span>
      </div>
      <div className="sourceCardFooter">
        <span>{source.organization}</span>
        <a href={source.url} target="_blank" rel="noreferrer">
          公式ページを開く
          <span aria-hidden="true"> ↗</span>
        </a>
      </div>
    </article>
  );
}
