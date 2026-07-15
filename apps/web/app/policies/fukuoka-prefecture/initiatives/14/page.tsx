import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "安心して子育てできる環境づくり｜数値目標",
  description:
    "福岡県総合計画の取組14に設定された4つの数値目標を、小児科医師、NICU、小児がん、児童虐待相談の基準値と条件・下限目標、実績未接続状態とともに確認できます。",
};

export default function Initiative14Page() {
  return <PolicyTargetDetail definition={policyTargetPage("14")} />;
}
