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

ready=false
for attempt in $(seq 1 18); do
  status="$(fetch_route "/" "$INDEX_FILE")"
  printf 'Attempt %02d: HTTP %s\n' "$attempt" "$status" >> "$REPORT"
  if [[ "$status" == "200" ]] \
    && grep --quiet --fixed-strings 'Jichi Insight' "$INDEX_FILE" \
    && grep --quiet --fixed-strings '全国47都道府県を探す' "$INDEX_FILE" \
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
  "全国47都道府県を、同じ品質段階で追う。" \
  "公式入口確認済み" \
  "政策計画入口索引済み" \
  "現行政策入口確認済み" \
  "入口確認の先を、6つの資料カテゴリで追う。" \
  "政策計画" \
  "実施計画" \
  "KPI・数値目標" \
  "年度評価" \
  "予算・決算" \
  "事業評価" \
  "47/47" \
  "公開中" \
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
  "宮城県の政策目標を、原文・期間・未設定までそのまま読む。" \
  "目標値の確認と、政策成果の評価を分ける。"

check_content "/municipalities/fukuoka-prefecture/" \
  "普通会計" \
  "まだ評価していないこと"

check_content "/data-quality/" \
  "件数ではなく、確認の深さを公開する。" \
  "データ不足を、点数で埋めません。"

printf '\nPhase 7 nationwide registry checks: PASS\n' >> "$REPORT"
printf 'Result: PASS\n' >> "$REPORT"
cat "$REPORT"
