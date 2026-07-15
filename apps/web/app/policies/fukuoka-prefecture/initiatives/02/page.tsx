import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "世界から選ばれる福岡県の実現｜数値目標",
  description:
    "福岡県総合計画の取組2に設定された7つの数値目標を、基準値、目標値、期間、欠損、実績未接続状態とともに確認できます。",
};

export default function Initiative02Page() {
  return <PolicyTargetDetail definition={policyTargetPage("02")} />;
}
