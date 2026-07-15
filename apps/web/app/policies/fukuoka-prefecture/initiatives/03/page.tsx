import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "ワンヘルスの推進｜数値目標",
  description:
    "福岡県総合計画の取組3に設定された数値目標を、当初値未設定、目標値、期間、実績未接続状態とともに確認できます。",
};

export default function Initiative03Page() {
  return <PolicyTargetDetail definition={policyTargetPage("03")} />;
}
