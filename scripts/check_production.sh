#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${JICHI_PRODUCTION_URL:-https://m-osugi1230.github.io/jichi-insight}"
REPORT="${JICHI_SMOKE_REPORT:-production-smoke-report.txt}"
INDEX_FILE="$(mktemp)"
CONTENT_FILE="$(mktemp)"
trap 'rm -f "$INDEX_FILE" "$CONTENT_FILE"' EXIT

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
    && grep --quiet --fixed-strings '全国47都道府県から探す' "$INDEX_FILE" \
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
  "/municipalities/hokkaido/"
  "/municipalities/miyagi/"
  "/municipalities/tokyo/"
  "/municipalities/fukuoka-prefecture/"
  "/sources/"
  "/robots.txt"
  "/sitemap.xml"
  "/manifest.webmanifest"
)

printf '\nRoute checks:\n' >> "$REPORT"
for route in "${routes[@]}"; do
  status="$(fetch_route "$route" /dev/null)"
  printf '%-48s HTTP %s\n' "$route" "$status" >> "$REPORT"
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
  printf '\nContent check %-33s HTTP %s\n' "$route" "$status" >> "$REPORT"
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
  "47都道府県を、資料の深さから探す。" \
  "全国の入口整備" \
  "いま、深く読める4都道府県。" \
  "東京都の政策目標を見る" \
  "政策計画入口" \
  "確認したい資料の深さ" \
  "都道府県と、確認できる資料。" \
  "政策計画" \
  "実施計画" \
  "KPI・数値目標" \
  "年度評価" \
  "予算・決算" \
  "事業評価" \
  "自治体ページ公開中" \
  "公開状態" \
  "未公開"

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

check_content "/municipalities/hokkaido/" \
  "北海道の政策指標を、原文と期間から読む。" \
  "108 / 108のKPI本文Reviewedを完了"

check_content "/municipalities/miyagi/" \
  "目標と実績を、同じものにしない。" \
  "2つの目標を、混ぜない。" \
  "年度実績を、指標ごとに確かめる。"

check_content "/municipalities/tokyo/" \
  "東京都の政策目標を、値と条件を変えずに読む。" \
  "8目標・9系列" \
  "2 / 60ページをReviewed。" \
  "年度実績 未接続" \
  "政策評価 未判定" \
  "02 子育て PDFページ3-4"

check_content "/municipalities/fukuoka-prefecture/" \
  "普通会計" \
  "まだ評価していないこと"

check_content "/data-quality/" \
  "件数ではなく、確認の深さを公開する。" \
  "データ不足を、点数で埋めません。"

printf '\nPhase 7 nationwide registry checks: PASS\n' >> "$REPORT"
printf 'Phase 8 Tokyo partial Reviewed publication checks: PASS\n' >> "$REPORT"
printf 'Result: PASS\n' >> "$REPORT"
cat "$REPORT"
