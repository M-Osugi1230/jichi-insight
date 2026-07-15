import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";
export const metadata: Metadata = { title: "地域の活力向上｜数値目標", description: "福岡県総合計画の取組24に設定された移住支援事業とサテライトオフィスの2指標を確認できます。" };
export default function Initiative24Page() { return <PolicyTargetDetail definition={policyTargetPage("24")} />; }
