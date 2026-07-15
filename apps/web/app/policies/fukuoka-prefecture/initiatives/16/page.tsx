import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "高齢者、障がいのある人への支援｜数値目標",
  description: "福岡県総合計画の取組16に設定された7つの固有数値目標を、高齢者活動、認知症、介護、障がい者収入、再掲範囲、実績未接続状態とともに確認できます。",
};

export default function Initiative16Page() {
  return <PolicyTargetDetail definition={policyTargetPage("16")} />;
}
