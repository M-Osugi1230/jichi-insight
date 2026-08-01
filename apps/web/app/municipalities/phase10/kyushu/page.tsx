import type { Metadata } from "next";

import { Phase10RegionalDepthPage } from "@/components/Phase10RegionalDepthPage";
import { loadPhase10KyushuDepth } from "@/lib/phase10RegionalDepth";

export const metadata: Metadata = {
  title: "Phase 10 九州｜6県の年度実績・予算・決算・事業・監査",
  description:
    "佐賀県、長崎県、熊本県、大分県、宮崎県、鹿児島県の年度実績、予算、決算、重点事業、監査の公式資料と境界を公開します。",
};

export const dynamic = "force-static";

export default function Phase10KyushuPage() {
  return (
    <Phase10RegionalDepthPage
      reviews={loadPhase10KyushuDepth()}
      title="九州6県も、同じ5層をReviewed化。"
      description="佐賀県、長崎県、熊本県、大分県、宮崎県、鹿児島県について、年度実績、予算、決算、重点事業、監査の公式資料を確認しました。沖縄県と福岡県は地域拠点として別途Reviewed済みです。"
      subjectLabel="福岡県・沖縄県を除く九州6県です。"
      boundaryTitle="新計画、骨格予算、旧決算年度を明示する。"
      boundaries={[
        "長崎県は新総合計画の初回確定実績と肉付け後予算を待ちます。",
        "長崎県の確認済み決算審査は対象年度を明示し、令和6年度決算として誤表示しません。",
        "鹿児島県の行政評価制度入口を県ビジョン全体の成果評価として扱いません。",
        "大分県の旧プラン評価と現行ビジョン2024を分離します。",
      ]}
      nextTitle="5層の公式資料レビューは47都道府県まで到達。"
      nextDescription="次の完了条件は、目標単位の年度実績・金額・事業接続と、契約・議会・監査・首長公約の同一粒度化です。"
    />
  );
}
