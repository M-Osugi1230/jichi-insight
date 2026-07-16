#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${JICHI_PRODUCTION_URL:-https://m-osugi1230.github.io/jichi-insight}"
REPORT="${JICHI_POLICY_SMOKE_REPORT:-policy-targets-21-26-smoke-report.txt}"
TEMP_FILE="$(mktemp)"
trap 'rm -f "$TEMP_FILE"' EXIT

: > "$REPORT"
printf 'Jichi Insight policy targets 21-26 production smoke\n' >> "$REPORT"
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

check_page "/policies/" \
  "取組1から26の指標1から118まで" \
  "取組27から30の数値目標"

check_page "/data-quality/" \
  "取組1から26の基準値・目標値118件"

check_page "/policies/fukuoka-prefecture/initiatives/21/" \
  "豊かな自然環境の保全と快適な生活環境の創造" \
  "水質環境基準の達成率" \
  "BOD 3mg/L以下"

check_page "/policies/fukuoka-prefecture/initiatives/22/" \
  "環境に負荷をかけない社会への移行" \
  "一般廃棄物の総排出量" \
  "5,510千t"

check_page "/policies/fukuoka-prefecture/initiatives/23/" \
  "防災・減災・県土強靱化" \
  "道路橋の耐震化率" \
  "土砂災害特別警戒区域内の住宅戸数"

check_page "/policies/fukuoka-prefecture/initiatives/24/" \
  "地域の活力向上" \
  "地方創生移住支援事業" \
  "サテライトオフィス"

check_page "/policies/fukuoka-prefecture/initiatives/25/" \
  "県内各地域の振興" \
  "無電柱化整備延長" \
  "重要港湾の耐震強化岸壁整備率"

check_page "/policies/fukuoka-prefecture/initiatives/26/" \
  "生活と産業を支える基盤の整備" \
  "法定有効年数超過率" \
  "インターネットの接続率"

printf '\nResult: PASS\n' >> "$REPORT"
cat "$REPORT"
