import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "デジタル社会の実現｜数値目標",
  description:
    "福岡県総合計画の取組5に設定された2つの数値目標を、基準値、目標値、期間、参考値、実績未接続状態とともに確認できます。",
};

export default function Initiative05Page() {
  return <PolicyTargetDetail definition={policyTargetPage("05")} />;
}
