import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "豊かな自然環境の保全と快適な生活環境の創造｜数値目標",
  description: "福岡県総合計画の取組21に設定された2つの数値目標を、保護地域、水質条件、単位不一致、実績未接続状態とともに確認できます。",
};

export default function Initiative21Page() {
  return <PolicyTargetDetail definition={policyTargetPage("21")} />;
}
