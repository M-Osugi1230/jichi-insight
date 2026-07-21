#!/usr/bin/env python3
"""Integrate the reviewed Okinawa anchor into nationwide Web and validation."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"Missing integration anchor in {path}: {old[:80]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def integrate_coverage_explorer() -> None:
    path = "apps/web/components/CoverageExplorer.tsx"
    replace_once(
        path,
        'import { osakaIndicatorStats } from "@/lib/osakaIndicators";\n',
        'import { okinawaIndicatorStats } from "@/lib/okinawaIndicators";\n'
        'import { osakaIndicatorStats } from "@/lib/osakaIndicators";\n',
    )
    replace_once(
        path,
        '  const kagawaReviewed =\n'
        '    prefectureCode === "37" && kagawaIndicatorStats.reviewedIndicators > 0;\n',
        '  const kagawaReviewed =\n'
        '    prefectureCode === "37" && kagawaIndicatorStats.reviewedIndicators > 0;\n'
        '  const okinawaReviewed =\n'
        '    prefectureCode === "47" && okinawaIndicatorStats.reviewedIndicators > 0;\n',
    )
    replace_once(
        path,
        '      hiroshimaReviewed ||\n'
        '      kagawaReviewed\n',
        '      hiroshimaReviewed ||\n'
        '      kagawaReviewed ||\n'
        '      okinawaReviewed\n',
    )
    replace_once(
        path,
        '                            : record.prefecture_code === "37"\n'
        '                              ? `延長後計画の${kagawaIndicatorStats.reviewedIndicators}指標・Evidence ${kagawaIndicatorStats.evidencePackets}件をReviewed済み。次に行政評価と年度実績を接続する。`\n'
        '                              : inventory?.next_action ?? "資料インベントリを確認中";\n',
        '                            : record.prefecture_code === "37"\n'
        '                              ? `延長後計画の${kagawaIndicatorStats.reviewedIndicators}指標・Evidence ${kagawaIndicatorStats.evidencePackets}件をReviewed済み。次に行政評価と年度実績を接続する。`\n'
        '                              : record.prefecture_code === "47"\n'
        '                                ? `現行中期計画の${okinawaIndicatorStats.reviewedIndicators}指標（主要${okinawaIndicatorStats.majorIndicators}・成果${okinawaIndicatorStats.outcomeIndicators}）をReviewed済み。次に過年度PDCA実績を定義照合する。`\n'
        '                                : inventory?.next_action ?? "資料インベントリを確認中";\n',
    )


def integrate_municipalities_page() -> None:
    path = "apps/web/app/municipalities/page.tsx"
    replace_once(
        path,
        'import { osakaIndicatorStats } from "@/lib/osakaIndicators";\n',
        'import { okinawaIndicatorStats } from "@/lib/okinawaIndicators";\n'
        'import { osakaIndicatorStats } from "@/lib/osakaIndicators";\n',
    )
    replace_once(path, "いま、深く読める8都道府県。", "いま、深く読める9都道府県。")
    replace_once(
        path,
        '              <Link href="/municipalities/kagawa">香川県の計画指標を見る →</Link>\n'
        '            </article>\n'
        '          </div>\n',
        '              <Link href="/municipalities/kagawa">香川県の計画指標を見る →</Link>\n'
        '            </article>\n'
        '            <article className={`${styles.deepDiveCard} ${styles.miyagi}`}>\n'
        '              <div><span>47 / 沖縄県</span><StatusBadge label="中期計画指標全件Reviewed" tone="verified" /></div>\n'
        '              <h3>375指標を二層で読む。</h3>\n'
        '              <dl>\n'
        '                <div><dt>主要指標</dt><dd>{okinawaIndicatorStats.majorIndicators}</dd></div>\n'
        '                <div><dt>成果指標</dt><dd>{okinawaIndicatorStats.outcomeIndicators}</dd></div>\n'
        '                <div><dt>離島指標</dt><dd>{okinawaIndicatorStats.islandIndicators}</dd></div>\n'
        '                <div><dt>Evidence</dt><dd>{okinawaIndicatorStats.evidencePackets}</dd></div>\n'
        '              </dl>\n'
        '              <p>主要指標と成果指標、離島・SDGs属性、定性目標、全国値を分離し、前期PDCA実績を自動接続しません。</p>\n'
        '              <Link href="/municipalities/okinawa">沖縄県の中期計画指標を見る →</Link>\n'
        '            </article>\n'
        '          </div>\n',
    )
    replace_once(
        path,
        '                (category === "kpi_source" && kagawaIndicatorStats.reviewedIndicators > 0 ? 1 : 0);\n',
        '                (category === "kpi_source" && kagawaIndicatorStats.reviewedIndicators > 0 ? 1 : 0) +\n'
        '                (category === "kpi_source" && okinawaIndicatorStats.reviewedIndicators > 0 ? 1 : 0);\n',
    )
    replace_once(
        path,
        "公開済み8地域と、次に資料を深掘りする1地域を示します。",
        "9地域すべてでEvidence付き数値目標を公開し、次は年度実績・予算・事業評価との接続を進めます。",
    )
    replace_once(
        path,
        '                              : item.prefecture_code === "40"\n'
        '                                ? "/municipalities/fukuoka-prefecture"\n'
        '                                : null;\n',
        '                              : item.prefecture_code === "40"\n'
        '                                ? "/municipalities/fukuoka-prefecture"\n'
        '                                : item.prefecture_code === "47"\n'
        '                                  ? "/municipalities/okinawa"\n'
        '                                  : null;\n',
    )
    replace_once(
        path,
        '<p className="eyebrow">Phase 8</p>\n'
        '            <h2>全国の入口から、目標・実績・予算の接続へ。</h2>\n'
        '            <p>次の重点は、各地域の拠点自治体でKPI、年度評価、予算・決算、事業評価を同じ品質基準でつなぐことです。</p>',
        '<p className="eyebrow">Phase 8 complete / Phase 9 in progress</p>\n'
        '            <h2>9地域の目標レビューから、残り38県と年度実績の接続へ。</h2>\n'
        '            <p>地域拠点9県のEvidence付き目標レビューは完了しました。Phase 9では残る38県の数値目標索引と、実績・予算・事業評価の接続を進めます。</p>',
    )


def integrate_sitemap() -> None:
    replace_once(
        "apps/web/app/sitemap.ts",
        '  "/municipalities/kagawa",\n  "/municipalities/fukuoka-prefecture",\n',
        '  "/municipalities/kagawa",\n  "/municipalities/okinawa",\n  "/municipalities/fukuoka-prefecture",\n',
    )


def integrate_static_validation() -> None:
    path = "scripts/validate_static_export.py"
    replace_once(
        path,
        '    "municipalities/kagawa/index.html",\n    "municipalities/fukuoka-prefecture/index.html",\n',
        '    "municipalities/kagawa/index.html",\n    "municipalities/okinawa/index.html",\n    "municipalities/fukuoka-prefecture/index.html",\n',
    )
    replace_once(path, '        "いま、深く読める8都道府県。",\n', '        "いま、深く読める9都道府県。",\n')
    replace_once(
        path,
        '        "香川県の計画指標を見る",\n',
        '        "香川県の計画指標を見る",\n        "沖縄県の中期計画指標を見る",\n',
    )
    replace_once(
        path,
        '    "municipalities/fukuoka-prefecture/index.html": [\n',
        '    "municipalities/okinawa/index.html": [\n'
        '        "沖縄県の375指標を、主要指標と成果指標に分けて読む。",\n'
        '        "Reviewed指標",\n'
        '        "主要指標",\n'
        '        "成果指標",\n'
        '        "原資料の単位差を、推測で直さない。",\n'
        '        "375指標を、階層・政策・値・属性から探す。",\n'
        '        "政策評価 未判定",\n'
        '    ],\n'
        '    "municipalities/fukuoka-prefecture/index.html": [\n',
    )


def integrate_production_smoke() -> None:
    path = "scripts/check_production.sh"
    replace_once(
        path,
        '  "/municipalities/kagawa/"\n  "/municipalities/fukuoka-prefecture/"\n',
        '  "/municipalities/kagawa/"\n  "/municipalities/okinawa/"\n  "/municipalities/fukuoka-prefecture/"\n',
    )
    replace_once(path, '  "いま、深く読める8都道府県。" \\\n', '  "いま、深く読める9都道府県。" \\\n')
    replace_once(
        path,
        '  "香川県の計画指標を見る" \\\n',
        '  "香川県の計画指標を見る" \\\n  "沖縄県の中期計画指標を見る" \\\n',
    )
    replace_once(
        path,
        'check_content "/municipalities/fukuoka-prefecture/" \\\n',
        'check_content "/municipalities/okinawa/" \\\n'
        '  "沖縄県の375指標を、主要指標と成果指標に分けて読む。" \\\n'
        '  "主要指標" \\\n'
        '  "成果指標" \\\n'
        '  "原資料の単位差を、推測で直さない。" \\\n'
        '  "375指標を、階層・政策・値・属性から探す。" \\\n'
        '  "政策評価 未判定"\n\n'
        'check_content "/municipalities/fukuoka-prefecture/" \\\n',
    )
    replace_once(
        path,
        "Phase 8 Tokyo, Aichi, Osaka, Hiroshima and Kagawa reviewed publication checks: PASS",
        "Phase 8 all nine regional anchors reviewed publication checks: PASS",
    )


def main() -> None:
    integrate_coverage_explorer()
    integrate_municipalities_page()
    integrate_sitemap()
    integrate_static_validation()
    integrate_production_smoke()


if __name__ == "__main__":
    main()
