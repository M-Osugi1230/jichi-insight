import type { Metadata } from "next";

import { PolicyTargetDetail } from "@/components/PolicyTargetDetail";
import { policyTargetPage } from "@/lib/policyTargets";

export const metadata: Metadata = {
  title: "健康づくり、安心で質の高い医療の提供｜数値目標",
  description:
    "福岡県総合計画の取組12に設定された5つの数値目標を、健康寿命の条件型目標、死亡率の上限目標、医薬品普及率、看護職員就職者数とともに確認できます。",
};

export default function Initiative12Page() {
  return <PolicyTargetDetail definition={policyTargetPage("12")} />;
}
