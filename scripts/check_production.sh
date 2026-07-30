#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${JICHI_PRODUCTION_URL:-https://m-osugi1230.github.io/jichi-insight}"
REPORT="${JICHI_SMOKE_REPORT:-production-smoke-report.txt}"
INDEX_FILE="$(mktemp)"
CONTENT_FILE="$(mktemp)"
trap 'rm -f "$INDEX_FILE" "$CONTENT_FILE"' EXIT

REVIEWED_TOTAL="$(
  python - <<'PY'
import json
from pathlib import Path

root = Path.cwd()
catalog = root / "data/catalog"
phase9 = json.loads((catalog / "phase9_review_summary.json").read_text(encoding="utf-8"))
manifest_fields = [
    ("hokkaido_policy_review_manifest.json", "reviewed_indicator_count"),
    ("miyagi_policy_review_manifest.json", "reviewed_target_group_count"),
    ("tokyo_policy_target_review_manifest.json", "reviewed_target_card_count"),
    ("aichi_policy_indicator_review_manifest.json", "reviewed_indicator_row_count"),
    ("osaka_beyond_expo_indicator_review_manifest.json", "reviewed_indicator_row_count"),
    ("hiroshima_revised_vision_indicator_review_manifest.json", "reviewed_indicator_count"),
    ("kagawa_extended_plan_indicator_review_manifest.json", "reviewed_indicator_count"),
    ("okinawa_midterm_indicator_review_manifest.json", "reviewed_indicator_count"),
]
anchor_total = sum(
    json.loads((catalog / filename).read_text(encoding="utf-8"))[field]
    for filename, field in manifest_fields
)
fukuoka_total = sum(
    len(json.loads(path.read_text(encoding="utf-8"))["items"])
    for path in (root / "data/entities/policy").glob(
        "fukuoka_prefecture_initiative_*_targets.json"
    )
)
print(f"{phase9['reviewed_target_statement_count'] + anchor_total + fukuoka_total:,}")
PY
)"

: > "$REPORT"
printf 'Jichi Insight production smoke test\n' >> "$REPORT"
printf 'URL: %s/\n' "$BASE_URL" >> "$REPORT"
printf 'Checked at: %s\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$REPORT"

fetch_route() {
  local route="$1"
  local output="$2"
  curl --silent --show-error --location --output "$output" --write-out '%{http_code}' "$BASE_URL$route" || true
}

normalize_html_file() {
  local path="$1"
  python - "$path" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
content = path.read_text(encoding="utf-8")
path.write_text(re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL), encoding="utf-8")
PY
}

ready=false
for attempt in $(seq 1 18); do
  status="$(fetch_route "/" "$INDEX_FILE")"
  printf 'Attempt %02d: HTTP %s\n' "$attempt" "$status" >> "$REPORT"
  if [[ "$status" == "200" ]]; then
    normalize_html_file "$INDEX_FILE"
  fi
  if [[ "$status" == "200" ]] \
    && grep --quiet --fixed-strings 'Jichi Insight' "$INDEX_FILE" \
    && grep --quiet --fixed-strings '47都道府県から探す' "$INDEX_FILE" \
    && grep --quiet --fixed-strings "${REVIEWED_TOTAL}件" "$INDEX_FILE" \
    && grep --quiet --fixed-strings '/jichi-insight/_next/' "$INDEX_FILE"; then
    ready=true
    break
  fi
  sleep 10
done

if [[ "$ready" != "true" ]]; then
  printf '\nProduction home page did not become ready.\n' >> "$REPORT"
  cat "$REPORT"
  exit 1
fi

routes=(
  "/about/"
  "/corrections/"
  "/data-quality/"
  "/methodology/"
  "/municipalities/"
  "/municipalities/phase9/"
  "/municipalities/hokkaido/"
  "/municipalities/miyagi/"
  "/municipalities/tokyo/"
  "/municipalities/aichi/"
  "/municipalities/osaka/"
  "/municipalities/hiroshima/"
  "/municipalities/kagawa/"
  "/municipalities/okinawa/"
  "/municipalities/fukuoka-prefecture/"
  "/sources/"
  "/robots.txt"
  "/sitemap.xml"
  "/manifest.webmanifest"
)

if [[ -f data/catalog/published_prefecture_pages.json ]]; then
  while IFS= read -r route; do
    routes+=("${route%/}/")
  done < <(
    python - <<'PY'
import json
from pathlib import Path

registry = json.loads(
    Path("data/catalog/published_prefecture_pages.json").read_text(encoding="utf-8")
)
for record in registry["records"]:
    print(record["route"])
PY
  )
fi

printf '\nRoute checks:\n' >> "$REPORT"
printf '%s\n' "${routes[@]}" | awk '!seen[$0]++' | while IFS= read -r route; do
  status="$(fetch_route "$route" /dev/null)"
  printf '%-55s HTTP %s\n' "$route" "$status" >> "$REPORT"
  if [[ "$status" != "200" ]]; then
    cat "$REPORT"
    exit 1
  fi
done

check_content() {
  local route="$1"
  shift
  local status
  status="$(fetch_route "$route" "$CONTENT_FILE")"
  printf '\nContent check %-40s HTTP %s\n' "$route" "$status" >> "$REPORT"
  if [[ "$status" != "200" ]]; then
    cat "$REPORT"
    exit 1
  fi
  normalize_html_file "$CONTENT_FILE"

  local required
  for required in "$@"; do
    if grep --quiet --fixed-strings "$required" "$CONTENT_FILE"; then
      printf '  PASS %s\n' "$required" >> "$REPORT"
    else
      printf '  FAIL %s\n' "$required" >> "$REPORT"
      cat "$REPORT"
      exit 1
    fi
  done
}

check_content "/municipalities/" \
  "47都道府県の目標原文を、Evidenceから探す。" \
  "PHASE 9 COMPLETE" \
  "${REVIEWED_TOTAL}件" \
  "読みたいデータの深さ" \
  "47都道府県の統合索引。" \
  "Reviewed" \
  "Evidence Packet" \
  "目標" \
  "実績" \
  "予算" \
  "事業" \
  "契約" \
  "根拠を読む" \
  "公式計画"

printf '\nPrefecture coverage checks:\n' >> "$REPORT"
while IFS= read -r prefecture_name; do
  if grep --quiet --fixed-strings "$prefecture_name" "$CONTENT_FILE"; then
    printf '  PASS %s\n' "$prefecture_name" >> "$REPORT"
  else
    printf '  FAIL %s\n' "$prefecture_name" >> "$REPORT"
    cat "$REPORT"
    exit 1
  fi
done < <(
  python - <<'PY'
import json
from pathlib import Path

registry = json.loads(Path("data/catalog/prefecture_coverage.json").read_text(encoding="utf-8"))
for record in registry["records"]:
    print(record["name"])
PY
)

check_content "/municipalities/phase9/" \
  "38県の数値目標を、原文とEvidenceから読む。" \
  "Evidence coverage" \
  "比較不能を保持" \
  "政策評価は未判定"

if [[ -f data/catalog/phase9_review_summary.json ]]; then
  while IFS=$'\t' read -r route name plan_title; do
    check_content "${route%/}/" \
      "$name" \
      "$plan_title" \
      "Reviewed / Not comparable" \
      "Evidence ID" \
      "比較対象外の理由"
  done < <(
    python - <<'PY'
import json
from pathlib import Path

summary = json.loads(Path("data/catalog/phase9_review_summary.json").read_text(encoding="utf-8"))
for record in summary["records"]:
    print(f"{record['route']}\t{record['name']}\t{record['plan_title']}")
PY
  )
fi

check_content "/municipalities/hokkaido/" \
  "北海道の政策指標を、原文と期間から読む。" \
  "108 / 108のKPI本文Reviewedを完了"

check_content "/municipalities/miyagi/" \
  "目標と実績を、同じものにしない。" \
  "2つの目標を、混ぜない。" \
  "年度実績を、指標ごとに確かめる。"

check_content "/municipalities/tokyo/" \
  "東京都の政策目標を、値と条件を変えずに読む。" \
  "304目標カード" \
  "60 / 60ページの政策目標カードReviewedを完了。" \
  "25政策分野・304目標カードを横断検索。" \
  "子供分野以外のグラフ点列は未正規化" \
  "年度実績 未接続" \
  "政策評価 未判定"

check_content "/municipalities/aichi/" \
  "愛知県の目標と年次現状値を、定義を変えずに読む。" \
  "56指標" \
  "62系列" \
  "現状値接続" \
  "再掲" \
  "目標改定" \
  "管理事業評価" \
  "政策評価 未判定"

check_content "/municipalities/osaka/" \
  "大阪府の戦略目標とWell-Beingを、同じ点数にしない。" \
  "83指標" \
  "91系列" \
  "名目GDP80兆円" \
  "客観KPI" \
  "主観・Well-Being" \
  "初回調査待ち" \
  "旧戦略の実績" \
  "政策評価 未判定"

check_content "/municipalities/hiroshima/" \
  "広島県の62指標を、改定後の定義と目標から読む。" \
  "Reviewed指標" \
  "現状値あり" \
  "Evidence ID" \
  "改定、未測定、定性目標を同じ数値にしない。" \
  "62指標を、分野・値・年度・出典から探す。" \
  "政策評価 未判定"

check_content "/municipalities/kagawa/" \
  "香川県の135指標を、延長前と延長後の目標から読む。" \
  "Reviewed指標" \
  "掲載位置" \
  "目標更新" \
  "計画延長を、単なる年度の置換にしない。" \
  "135指標を、名称・値・変更状態から探す。" \
  "政策評価 未判定"

check_content "/municipalities/okinawa/" \
  "沖縄県の375指標を、主要指標と成果指標に分けて読む。" \
  "主要指標" \
  "成果指標" \
  "原資料の単位差を、推測で直さない。" \
  "375指標を、階層・政策・値・属性から探す。" \
  "政策評価 未判定"

check_content "/municipalities/fukuoka-prefecture/" \
  "普通会計" \
  "まだ評価していないこと"

check_content "/data-quality/" \
  "件数ではなく、確認の深さを公開する。" \
  "${REVIEWED_TOTAL}件の内訳。" \
  "目標から契約までの現在地。" \
  "壊さない4つの境界。" \
  "データ不足を、点数で埋めません。"

printf '\nNationwide 47/47 reviewed publication checks: PASS\n' >> "$REPORT"
printf 'Phase 9 all 38 remaining prefectures reviewed publication checks: PASS\n' >> "$REPORT"
printf 'Phase 10 vertical linkage visibility checks: PASS\n' >> "$REPORT"
printf 'Result: PASS\n' >> "$REPORT"
cat "$REPORT"
