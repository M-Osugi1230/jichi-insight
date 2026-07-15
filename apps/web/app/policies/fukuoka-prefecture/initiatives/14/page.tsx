import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "文化芸術の振興｜数値目標",
  description: "福岡県総合計画の取組14に設定された3つの数値目標を、文化芸術鑑賞、美術館入館者、障がい者アート、実績未接続状態とともに確認できます。",
};

export default function Initiative14Page() {
  return <PolicyTargetDetail definition={policyTargetPage("14")} />;
}
