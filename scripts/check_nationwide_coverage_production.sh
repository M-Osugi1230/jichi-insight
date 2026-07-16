#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${JICHI_PRODUCTION_URL:-https://m-osugi1230.github.io/jichi-insight}"
REPORT="${JICHI_NATIONWIDE_SMOKE_REPORT:-nationwide-coverage-smoke-report.txt}"
TEMP_FILE="$(mktemp)"
trap 'rm -f "$TEMP_FILE"' EXIT

: > "$REPORT"
printf 'Jichi Insight nationwide coverage production smoke\n' >> "$REPORT"
printf 'URL: %s\n' "$BASE_URL" >> "$REPORT"
printf 'Checked at: %s\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$REPORT"

check_page() {
  local route="$1"
  shift
  local ready=false
  local status="000"

  for attempt in $(seq 1 18); do
    status="$(curl --silent --show-error --location --output "$TEMP_FILE" --write-out '%{http_code}' "$BASE_URL$route" || true)"
    printf '%s attempt %02d: HTTP %s\n' "$route" "$attempt" "$status" >> "$REPORT"

    if [[ "$status" == "200" ]]; then
      local missing=false
      local required
      for required in "$@"; do
        if ! grep --quiet --fixed-strings "$required" "$TEMP_FILE"; then
          missing=true
          break
        fi
      done
      if [[ "$missing" == "false" ]]; then
        ready=true
        break
      fi
    fi

    sleep 10
  done

  if [[ "$ready" != "true" ]]; then
    printf 'FAIL %s\n' "$route" >> "$REPORT"
    cat "$REPORT"
    exit 1
  fi

  local required
  for required in "$@"; do
    printf '  PASS %s\n' "$required" >> "$REPORT"
  done
}

check_page "/municipalities/" \
  "全国47都道府県を、同じ品質段階で追う。" \
  "全国登録" \
  "公式入口確認済み" \
  "総合計画索引済み" \
  "Reviewedデータ公開" \
  "北海道、宮城県、東京都、広島県、福岡県、沖縄県で計画資料の入口を確認。" \
  "公式URL候補" \
  "北海道" \
  "宮城県" \
  "東京都" \
  "愛知県" \
  "大阪府" \
  "広島県" \
  "香川県" \
  "福岡県" \
  "沖縄県" \
  "福岡市" \
  "北九州市"

check_page "/data-quality/" \
  "全国登録と、確認済み・Reviewed・公開済みを分ける。" \
  "47都道府県を共通コードと地域区分で登録。" \
  "自治体公式ホームページを手動確認した都道府県。" \
  "計画資料の公式入口を固定した都道府県。" \
  "本文・数値・期間・単位を人が照合済み。" \
  "公開ゲートと本番確認を通過したページ。" \
  "公式URL候補・未確認"

printf '\nResult: PASS\n' >> "$REPORT"
cat "$REPORT"
