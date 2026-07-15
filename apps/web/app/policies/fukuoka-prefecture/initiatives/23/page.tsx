import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";
export const metadata: Metadata = { title: "防災・減災・県土強靱化｜数値目標", description: "福岡県総合計画の取組23に設定された河川、橋梁、土砂災害区域の3指標を確認できます。" };
export default function Initiative23Page() { return <PolicyTargetDetail definition={policyTargetPage("23")} />; }
