import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";
export const metadata: Metadata = { title: "成長産業の創出｜数値目標", description: "福岡県総合計画の取組7に設定された4つの数値目標を、基準値、目標値、期間、実績未接続状態とともに確認できます。" };
export default function Initiative07Page() { return <PolicyTargetDetail definition={policyTargetPage("07")} />; }
