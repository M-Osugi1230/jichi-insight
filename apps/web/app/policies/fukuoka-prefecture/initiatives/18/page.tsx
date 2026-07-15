import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "人権が尊重される心豊かな社会づくり｜数値目標",
  description: "福岡県総合計画の取組18に設定された県人権啓発情報センター来館者数の目標を、平均期間と実績未接続状態とともに確認できます。",
};

export default function Initiative18Page() {
  return <PolicyTargetDetail definition={policyTargetPage("18")} />;
}
