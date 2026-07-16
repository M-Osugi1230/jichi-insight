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
  "全国47都道府県を、同じ品質段階で追う。" \
  "全国登録" \
  "公式入口確認済み" \
  "総合計画索引済み" \
  "現行計画確認済み" \
  "Reviewedデータ公開" \
  "2050東京戦略 ～東京 もっとよくなる～" \
  "Beyond EXPO 2025" \
  "「人生100年時代のフロンティア県・香川」実現計画" \
  "新・沖縄21世紀ビジョン基本計画（沖縄振興計画）" \
  "Reviewed化は、北海道から始める。" \
  "Reviewed基準実装" \
  "Reviewed化作業中" \
  "指標関係Reviewed・KPI本文抽出中" \
  "指標1〜52をEvidence Packet付きでReviewed化済み。" \
  "残る56指標" \
  "指標53〜60（教育・学び）" \
  "作業待ち" \
  "北海道の108指標から、全国Reviewed化を開始する。" \
  "公式URL候補" \
  "北海道" "宮城県" "東京都" "愛知県" "大阪府" "広島県" "香川県" "福岡県" "沖縄県" "福岡市" "北九州市"

check_absent "/municipalities/" "「未来の東京」戦略"
check_absent "/municipalities/" "将来ビジョン・大阪"
check_absent "/municipalities/" "大阪の再生・成長に向けた新戦略"

check_page "/data-quality/" \
  "全国登録、計画入口、現行性、Reviewed、公開済みを分ける。" \
  "47都道府県を共通コードと地域区分で登録。" \
  "公式計画を見つけた件数と、Reviewedに使える件数を分ける。" \
  "北海道指標PDF" \
  "北海道は指標1〜52をReviewed化し、残る56指標を抽出中。" \
  "北海道指標位置" \
  "北海道複数分野参照" \
  "北海道Reviewed指標" \
  "指標1〜52を一次資料と照合。残り56件は未Reviewed。" \
  "北海道KPI Evidence" \
  "Reviewed指標すべてにEvidence Packetを付与。" \
  "目標設定あり" \
  "条件目標" \
  "具体値を補わず、前年比較などの原文条件を保持。" \
  "累計系列" \
  "期間累計と各時点までの累計到達値を分離。" \
  "目標未設定" \
  "「―」を0へ変換せず、nullと原文説明で保持。" \
  "現状値なし" \
  "比較注意あり" \
  "全件完了まで公開昇格しません。" \
  "公式URL候補・未確認"

printf '\nResult: PASS\n' >> "$REPORT"
cat "$REPORT"
