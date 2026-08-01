import type { Metadata } from "next";

import { Phase10RegionalDepthPage } from "@/components/Phase10RegionalDepthPage";
import { loadPhase10ShikokuDepth } from "@/lib/phase10RegionalDepth";

export const metadata: Metadata = {
  title: "Phase 10 四国｜3県の年度実績・予算・決算・事業・監査",
  description:
    "徳島県、愛媛県、高知県の年度実績、予算、決算、重点事業、監査の公式資料と境界を公開します。",
};

export const dynamic = "force-static";

export default function Phase10ShikokuPage() {
  return (
    <Phase10RegionalDepthPage
      reviews={loadPhase10ShikokuDepth()}
      title="四国3県も、同じ5層をReviewed化。"
      description="徳島県、愛媛県、高知県について、年度実績、予算、決算、重点事業、監査の公式資料を確認しました。年度版や速報値の違いを保持します。"
      subjectLabel="Phase 8拠点の香川県を除く四国3県です。"
      boundaryTitle="速報、確報、年度版の違いを残す。"
      boundaries={[
        "愛媛県のKGI速報・確報と県民意識を一つの達成率へ統合しません。",
        "高知県の年度版KPI変更を版管理します。",
        "徳島県の旧地方創生戦略と現行計画を分離します。",
        "主要事業一覧が全事業を網羅するとはみなしません。",
      ]}
      nextTitle="資料の存在確認から、政策系列の照合へ進む。"
      nextDescription="目標、実績、事業、予算、決算の定義・期間・対象範囲が一致した場合のみ、同じ政策系列として接続します。"
    />
  );
}
