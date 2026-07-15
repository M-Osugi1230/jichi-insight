import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "スポーツ立県福岡の実現｜数値目標",
  description: "福岡県総合計画の取組13に設定された2つの固有数値目標を、スポーツイベント、障がい者参加、再掲指標、実績未接続状態とともに確認できます。",
};

export default function Initiative13Page() {
  return <PolicyTargetDetail definition={policyTargetPage("13")} />;
}
