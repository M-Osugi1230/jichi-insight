import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "次代を担う「人財」の育成｜数値目標",
  description:
    "福岡県総合計画の取組1に設定された10の数値目標を、基準値、目標値、期間、実績未接続状態とともに確認できます。",
};

export default function Initiative01Page() {
  return <PolicyTargetDetail definition={policyTargetPage("01")} />;
}
