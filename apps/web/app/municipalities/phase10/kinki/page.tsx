import type { Metadata } from "next";

import { Phase10RegionalDepthPage } from "@/components/Phase10RegionalDepthPage";
import { loadPhase10KinkiDepth } from "@/lib/phase10RegionalDepth";

export const metadata: Metadata = {
  title: "Phase 10 近畿｜6府県の年度実績・予算・決算・事業・監査",
  description:
    "三重県、滋賀県、京都府、兵庫県、奈良県、和歌山県の年度実績、予算、決算、重点事業、監査の公式資料と境界を公開します。",
};

export const dynamic = "force-static";

export default function Phase10KinkiPage() {
  return (
    <Phase10RegionalDepthPage
      reviews={loadPhase10KinkiDepth()}
      title="近畿6府県も、同じ5層をReviewed化。"
      description="三重県、滋賀県、京都府、兵庫県、奈良県、和歌山県について、年度実績、予算、決算、重点事業、監査の公式資料を確認しました。Reviewedは政策目標との直接接続を意味しません。"
      subjectLabel="Phase 8拠点の大阪府を除く近畿6府県です。"
      boundaryTitle="新計画初年度と旧計画評価を混ぜない。"
      boundaries={[
        "和歌山県の新総合計画は初年度のため、通年の確定実績を待ちます。",
        "兵庫県の年度途中モニタリングを確定実績として扱いません。",
        "奈良県の年度版政策集と重点課題評価を同一年度として扱いません。",
        "予算、決算、事業費、契約額を別レコードで保持します。",
      ]}
      nextTitle="5層の公式資料入口は全47都道府県で揃いました。"
      nextDescription="次は政策目標と年度実績、事業、金額を一対一で照合し、契約・議会・監査・首長公約まで接続します。"
    />
  );
}
