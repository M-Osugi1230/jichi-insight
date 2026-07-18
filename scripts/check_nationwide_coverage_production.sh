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
  "北海道108指標を全件Reviewed化。次は宮城県。" \
  "Reviewed基準実装" \
  "Reviewed化作業中" \
  "KPI位置確認済み・本文レビュー中" \
  "全108指標とEvidence Packet 108件をReviewed化済み。" \
  "128目標グループ・149系列" \
  "目標グループ1〜23" \
  "複数系列17グループ" \
  "北海道108指標のReviewed完了。次は宮城県の資料固定へ。" \
  "公式URL候補" \
  "北海道" "宮城県" "東京都" "愛知県" "大阪府" "広島県" "香川県" "福岡県" "沖縄県" "福岡市" "北九州市"

check_absent "/municipalities/" "「未来の東京」戦略"
check_absent "/municipalities/" "将来ビジョン・大阪"
check_absent "/municipalities/" "大阪の再生・成長に向けた新戦略"
check_absent "/municipalities/" "一意指標数と掲載行数を確定する"

check_page "/municipalities/hokkaido/" \
  "北海道の政策指標を、原文と期間から読む。" \
  "108 / 108のKPI本文Reviewedを完了。次は年度実績との接続。" \
  "食から歴史・文化・スポーツまで。" \
  "自然・環境" \
  "エゾシカの個体数指数" \
  "歴史・文化・スポーツ" \
  "北海道博物館の利用者数" \
  "本道出身のオリンピック･パラリンピック出場者数" \
  "本道出身者のオリンピック･パラリンピックメダル総獲得数" \
  "年度実績へ接続済み" \
  "目標を確認したことと、成果を確認したことは別です。" \
  "達成率や政策評価は表示しません。"

check_absent "/municipalities/hokkaido/" "108指標すべての完了ではありません"
check_absent "/municipalities/hokkaido/" "指標109〜108"

check_page "/data-quality/" \
  "全国登録、計画入口、現行性、Reviewed、公開済みを分ける。" \
  "47都道府県を共通コードと地域区分で登録。" \
  "公式計画を見つけた件数と、Reviewedに使える件数を分ける。" \
  "北海道指標PDF" \
  "福岡県と北海道を全国展開のデータ・Evidence Packet基準として使用。" \
  "宮城県政策資料" \
  "うちReviewed済み3件。評価原案は確定版と分離。" \
  "宮城県政策体系" \
  "基本方向・政策・取組。復興取組4分野は別系統。" \
  "宮城県KPI位置" \
  "目標グループ。個別系列は149件、掲載5ページ。" \
  "宮城県複数系列" \
  "追加系列21件。位置は確認済み、本文はReviewed化中。" \
  "宮城県政策Evidence" \
  "宮城県は128目標グループ・149系列のKPI本文をReviewed化中。" \
  "北海道指標位置" \
  "北海道複数分野参照" \
  "北海道Reviewed指標" \
  "指標1〜108を一次資料と照合し、未Reviewedは0件。" \
  "北海道KPI Evidence" \
  "全108指標にEvidence Packetを付与。" \
  "条件目標" \
  "前年比較、範囲、過去最高値などの原文条件を保持。" \
  "KPI本文は全件Reviewed済みで、年度実績接続は別ゲート。"

printf '\nResult: PASS\n' >> "$REPORT"
cat "$REPORT"
