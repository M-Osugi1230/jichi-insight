import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";
import { canonicalFor } from "@/lib/pageMetadata";

export const metadata: Metadata = {
  alternates: {
    canonical: canonicalFor("/policies/fukuoka-prefecture/initiatives/10"),
  },
  title: "地域と調和した観光産業の振興｜数値目標",
  description:
    "福岡県総合計画の取組10に設定された9つの固有数値目標を、旅行消費、SNS、宿泊、観光地域づくり法人の基準値と目標値、参考値、再掲範囲、実績未接続状態とともに確認できます。",
};

export default function Initiative10Page() {
  return <PolicyTargetDetail definition={policyTargetPage("10")} />;
}
