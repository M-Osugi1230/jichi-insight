import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "社会的・経済的に厳しい状況にある方への支援｜数値目標",
  description: "福岡県総合計画の取組17に設定された5つの数値目標を、DV支援、子どもの進学・中退、ひとり親就職、頻回受診改善、実績未接続状態とともに確認できます。",
};

export default function Initiative17Page() {
  return <PolicyTargetDetail definition={policyTargetPage("17")} />;
}
