#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${JICHI_PRODUCTION_URL:-https://m-osugi1230.github.io/jichi-insight}"
REPORT="${JICHI_NATIONWIDE_SMOKE_REPORT:-nationwide-coverage-smoke-report.txt}"
TEMP_FILE="$(mktemp)"
trap 'rm -f "$TEMP_FILE"' EXIT

readarray -t MIYAGI_STATE < <(
  python - <<'PY'
import json
from pathlib import Path

root = Path.cwd()
manifest = json.loads(
    (root / "data/catalog/miyagi_policy_review_manifest.json").read_text(encoding="utf-8")
)
print(manifest["reviewed_target_group_count"])
print(manifest["reviewed_indicator_series_count"])
print(manifest["actual_linked_indicator_series_count"])
print(manifest["actual_linkage_review_needed_series_count"])
print(manifest["actual_result_row_count"])

phase9 = json.loads(
    (root / "data/catalog/phase9_review_summary.json").read_text(encoding="utf-8")
)
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
    json.loads((root / "data/catalog" / filename).read_text(encoding="utf-8"))[field]
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
)

REVIEWED_GROUPS="${MIYAGI_STATE[0]}"
REVIEWED_SERIES="${MIYAGI_STATE[1]}"
LINKED_SERIES="${MIYAGI_STATE[2]}"
REVIEW_NEEDED_SERIES="${MIYAGI_STATE[3]}"
ANNUAL_ROWS="${MIYAGI_STATE[4]}"
REVIEWED_TOTAL="${MIYAGI_STATE[5]}"

: > "$REPORT"
printf 'Jichi Insight nationwide coverage production smoke\n' >> "$REPORT"
printf 'URL: %s\n' "$BASE_URL" >> "$REPORT"
printf 'Checked at: %s\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$REPORT"

check_page() {
  local route="$1"
  shift
  local status="000"

  for attempt in $(seq 1 18); do
    status="$(curl --silent --show-error --location --output "$TEMP_FILE" --write-out '%{http_code}' "$BASE_URL$route" || true)"
    printf '%s attempt %02d: HTTP %s\n' "$route" "$attempt" "$status" >> "$REPORT"
    if [[ "$status" == "200" ]]; then
      local missing=false
      for required in "$@"; do
        if ! grep --quiet --fixed-strings "$required" "$TEMP_FILE"; then
          missing=true
          break
        fi
      done
      if [[ "$missing" == "false" ]]; then
        for required in "$@"; do
          printf '  PASS %s\n' "$required" >> "$REPORT"
        done
        return 0
      fi
    fi
    sleep 10
  done

  printf 'FAIL %s\n' "$route" >> "$REPORT"
  cat "$REPORT"
  exit 1
}

check_absent() {
  local route="$1"
  local forbidden="$2"
  local status
  status="$(curl --silent --show-error --location --output "$TEMP_FILE" --write-out '%{http_code}' "$BASE_URL$route" || true)"
  if [[ "$status" != "200" ]] || grep --quiet --fixed-strings "$forbidden" "$TEMP_FILE"; then
    printf 'FAIL forbidden production text on %s: %s\n' "$route" "$forbidden" >> "$REPORT"
    cat "$REPORT"
    exit 1
  fi
  printf '  PASS absent %s\n' "$forbidden" >> "$REPORT"
}

check_page "/municipalities/" \
  "47都道府県の目標原文を、Evidenceから探す。" \
  "PHASE 9 COMPLETE" \
  "${REVIEWED_TOTAL}件" \
  "読みたいデータの深さ" \
  "47都道府県の統合索引。" \
  "年度実績を接続" \
  "財政値をReviewed" \
  "目標" "実績" "予算" "事業" "契約" \
  "北海道" "宮城県" "東京都" "愛知県" "大阪府" "広島県" "香川県" "福岡県" "沖縄県"

check_absent "/municipalities/" "「未来の東京」戦略"
check_absent "/municipalities/" "将来ビジョン・大阪"

check_page "/municipalities/hokkaido/" \
  "北海道の政策指標を、原文と期間から読む。" \
  "108 / 108のKPI本文Reviewedを完了。次は年度実績との接続。" \
  "目標を確認したことと、成果を確認したことは別です。" \
  "達成率や政策評価は表示しません。"

check_page "/municipalities/miyagi/" \
  "宮城県｜政策目標${REVIEWED_GROUPS}件・年度実績${ANNUAL_ROWS}件" \
  "目標と実績を、同じものにしない。" \
  "2つの目標を、混ぜない。" \
  "年度実績を、指標ごとに確かめる。" \
  "直接接続" \
  "対応要確認" \
  "人口の社会増減（人）" \
  "暮らしの満足度（宮城で暮らして良かったと思う県民の割合）（%）" \
  "健康寿命（日常生活に制限のない期間の平均）（男性）（年）" \
  "健康寿命（日常生活に制限のない期間の平均）（女性）（年）" \
  "ここから先は、まだ評価しない。"

check_absent "/municipalities/miyagi/" "達成率を算出済み"
check_absent "/municipalities/miyagi/" "政策評価済み"

check_page "/data-quality/" \
  "件数ではなく、確認の深さを公開する。" \
  "${REVIEWED_TOTAL}件の内訳。" \
  "目標から契約までの現在地。" \
  "宮城県では${LINKED_SERIES}系列を直接接続し、${REVIEW_NEEDED_SERIES}系列を要確認" \
  "データ不足を、点数で埋めません。"

printf '\nResult: PASS\n' >> "$REPORT"
cat "$REPORT"
