import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "外国人材に選ばれる地域づくり｜数値目標",
  description: "福岡県総合計画の取組19に設定された3つの数値目標を、留学生就職、国際交流、国際環境協力、実績未接続状態とともに確認できます。",
};

export default function Initiative19Page() {
  return <PolicyTargetDetail definition={policyTargetPage("19")} />;
}
