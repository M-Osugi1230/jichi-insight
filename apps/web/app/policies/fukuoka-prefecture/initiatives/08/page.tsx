import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "中小企業の振興｜数値目標",
  description:
    "福岡県総合計画の取組8に設定された6つの数値目標を、生産性、業績、経営革新、技術移転の基準値と目標値、実績未接続状態とともに確認できます。",
};

export default function Initiative08Page() {
  return <PolicyTargetDetail definition={policyTargetPage("08")} />;
}
