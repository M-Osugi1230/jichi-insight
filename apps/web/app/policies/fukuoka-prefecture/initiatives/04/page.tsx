import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "移住定住の促進｜数値目標",
  description:
    "福岡県総合計画の取組4に設定された2つの数値目標を、基準値、目標値、期間、実績未接続状態とともに確認できます。",
};

export default function Initiative04Page() {
  return <PolicyTargetDetail definition={policyTargetPage("04")} />;
}
