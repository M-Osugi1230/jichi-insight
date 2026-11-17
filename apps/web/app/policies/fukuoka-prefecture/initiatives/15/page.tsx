import type { Metadata } from "next";
import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";
import { canonicalFor } from "@/lib/pageMetadata";

export const metadata: Metadata = {
  alternates: {
    canonical: canonicalFor("/policies/fukuoka-prefecture/initiatives/15"),
  },
  title: "ジェンダー平等の社会づくり｜数値目標",
  description:
    "福岡県総合計画の取組15に設定された3つの数値目標を、審議会委員、自治会長、県管理職の女性割合、実績未接続状態とともに確認できます。",
};

export default function Initiative15Page() {
  return <PolicyTargetDetail definition={policyTargetPage("15")} />;
}
