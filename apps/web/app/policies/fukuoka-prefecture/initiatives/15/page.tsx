import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "高齢者、障がいのある人への支援｜数値目標",
  description:
    "福岡県総合計画の取組15に設定された3つの数値目標を、低栄養、就業支援満足度、70歳まで働ける企業割合の条件・下限目標、実績未接続状態とともに確認できます。",
};

export default function Initiative15Page() {
  return <PolicyTargetDetail definition={policyTargetPage("15")} />;
}
