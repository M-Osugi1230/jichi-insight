import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";
export const metadata: Metadata = { title: "生活と産業を支える基盤の整備｜数値目標", description: "福岡県総合計画の取組26に設定された水道、設備、停電、インターネットの5指標を確認できます。" };
export default function Initiative26Page() { return <PolicyTargetDetail definition={policyTargetPage("26")} />; }
