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

ready=false
for attempt in $(seq 1 18); do
  status="$(curl --silent --show-error --location --output "$INDEX_FILE" --write-out '%{http_code}' "$BASE_URL/" || true)"
  printf 'Attempt %02d: HTTP %s\n' "$attempt" "$status" >> "$REPORT"
  if [[ "$status" == "200" ]] \
    && grep --quiet 'Jichi Insight' "$INDEX_FILE" \
    && grep --quiet '公開済み評価' "$INDEX_FILE" \
    && grep --quiet '/jichi-insight/_next/' "$INDEX_FILE"; then
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
  "/assemblies/"
  "/assemblies/fukuoka-prefecture/overseas-activities/"
  "/compare/"
  "/corrections/"
  "/data-quality/"
  "/executives/"
  "/executives/source-requests/"
  "/methodology/"
  "/municipalities/"
  "/municipalities/fukuoka-prefecture/"
  "/municipalities/fukuoka-city/"
  "/municipalities/kitakyushu-city/"
  "/policy-sources/"
  "/sources/"
  "/robots.txt"
  "/sitemap.xml"
  "/manifest.webmanifest"
)

printf '\nRoute checks:\n' >> "$REPORT"
for route in "${routes[@]}"; do
  status="$(curl --silent --show-error --location --output /dev/null --write-out '%{http_code}' "$BASE_URL$route" || true)"
  printf '%-58s HTTP %s\n' "$route" "$status" >> "$REPORT"
  if [[ "$status" != "200" ]]; then
    cat "$REPORT"
    exit 1
  fi
done

check_content() {
  local route="$1"
  shift
  local status
  status="$(curl --silent --show-error --location --output "$CONTENT_FILE" --write-out '%{http_code}' "$BASE_URL$route" || true)"
  printf '\nContent check %-43s HTTP %s\n' "$route" "$status" >> "$REPORT"
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

check_content "/data-quality/" \
  "首長分野は、任期・探索・公約資料・分割レビュー・評価を分ける。" \
  "Reviewed現職任期" \
  "公約資料の探索記録" \
  "安定した一次資料を未発見" \
  "登録済み公約原文資料" \
  "公約分割レビュー" \
  "個別公約レコード" \
  "照会案、送信、回答を別の進捗として公開する。" \
  "照会案・送信前" \
  "送信済み照会" \
  "回答受領"

check_content "/executives/" \
  "首長評価の前に、任期と公約の根拠を固定する。" \
  "公約資料の探索記録" \
  "未発見は、資料が存在しないという判定ではありません。" \
  "手動レビュー待ち" \
  "作成済み公約レコード" \
  "資料があることと、公約を評価できることは別です。"

check_content "/executives/source-requests/" \
  "照会案を作ったことと、送信したことを分ける。" \
  "照会案2件。送信済み0件。回答受領0件。" \
  "この文案は未送信です。" \
  "明示承認前は送信しません。"

check_content "/policy-sources/" \
  "集められる政策資料から、先に形にする。" \
  "計画から支出と成果まで、順番につなぐ。" \
  "登録済み政策資料" \
  "抽出準備済み" \
  "資料10件を登録しましたが、政策評価はまだ0件です。"

printf '\nResult: PASS\n' >> "$REPORT"
cat "$REPORT"
