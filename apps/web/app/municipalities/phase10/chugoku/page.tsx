import type { Metadata } from "next";

import { Phase10RegionalDepthPage } from "@/components/Phase10RegionalDepthPage";
import { loadPhase10ChugokuDepth } from "@/lib/phase10RegionalDepth";

export const metadata: Metadata = {
  title: "Phase 10 中国｜4県の年度実績・予算・決算・事業・監査",
  description:
    "鳥取県、島根県、岡山県、山口県の年度実績、予算、決算、重点事業、監査の公式資料と境界を公開します。",
};

export const dynamic = "force-static";

export default function Phase10ChugokuPage() {
  return (
    <Phase10RegionalDepthPage
      reviews={loadPhase10ChugokuDepth()}
      title="中国4県も、同じ5層をReviewed化。"
      description="鳥取県、島根県、岡山県、山口県について、年度実績、予算、決算、重点事業、監査の公式資料を確認しました。Reviewedは政策達成判定ではありません。"
      subjectLabel="Phase 8拠点の広島県を除く中国4県です。"
      boundaryTitle="満足度、会議資料、政策評価を同じ成果値にしない。"
      boundaries={[
        "岡山県の県民満足度は政策目標の達成率として扱いません。",
        "島根県の第1期・第2期計画の評価年度を分離します。",
        "鳥取県の会議資料は現行戦略版との対応を確認してから接続します。",
        "監査意見を政策の成功・失敗へ自動変換しません。",
      ]}
      nextTitle="公式資料の全国索引から、目標単位の接続へ進む。"
      nextDescription="政策・KPI、年度実績、重点事業、予算・決算の共通IDを作成し、根拠が一致したレコードだけをLinkedへ進めます。"
    />
  );
}
