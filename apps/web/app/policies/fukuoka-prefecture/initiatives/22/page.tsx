import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";
export const metadata: Metadata = { title: "環境に負荷をかけない社会への移行｜数値目標", description: "福岡県総合計画の取組22に設定された一般廃棄物総排出量の目標を確認できます。" };
export default function Initiative22Page() { return <PolicyTargetDetail definition={policyTargetPage("22")} />; }
