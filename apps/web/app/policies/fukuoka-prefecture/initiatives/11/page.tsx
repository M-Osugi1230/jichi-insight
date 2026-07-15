import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "雇用対策の充実、魅力ある職場づくり｜数値目標",
  description:
    "福岡県総合計画の取組11に設定された14の数値目標を、人材育成、就職支援、障がい者雇用、育児休業、働き方改革の基準値と目標値、実績未接続状態とともに確認できます。",
};

export default function Initiative11Page() {
  return <PolicyTargetDetail definition={policyTargetPage("11")} />;
}
