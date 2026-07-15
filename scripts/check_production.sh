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
  if [[ "$status" == "200" ]] && grep --quiet 'Jichi Insight' "$INDEX_FILE" && grep --quiet '公開済み評価' "$INDEX_FILE" && grep --quiet '/jichi-insight/_next/' "$INDEX_FILE"; then
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
  "/policies/"
  "/policies/fukuoka-prefecture/initiatives/01/"
  "/policies/fukuoka-prefecture/initiatives/02/"
  "/policies/fukuoka-prefecture/initiatives/03/"
  "/policies/fukuoka-prefecture/initiatives/04/"
  "/policies/fukuoka-prefecture/initiatives/05/"
  "/policies/fukuoka-prefecture/initiatives/06/"
  "/policies/fukuoka-prefecture/initiatives/07/"
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
  "政策体系、数値目標、年度実績、評価を別の段階として公開する。" \
  "Reviewed基本方向" \
  "Reviewed取組事項" \
  "Reviewed数値目標" \
  "取組1から7の基準値・目標値28件" \
  "年度実績へ接続済み" \
  "政策評価済み" \
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
check_content "/policies/" \
  "政策評価の前に、計画が何を目指すかを構造化する。" \
  "4つの基本方向と30の取組事項" \
  "取組1から7の指標1から28まで" \
  "数値目標10件" \
  "数値目標7件" \
  "数値目標1件" \
  "数値目標2件" \
  "数値目標4件" \
  "取組と目標の一覧と、実際の成果はまだ別々です。"
check_content "/policies/fukuoka-prefecture/initiatives/01/" \
  "次代を担う「人財」の育成" \
  "Reviewed数値目標" \
  "国民体育大会における男女総合成績順位" \
  "年次値と累計値をそのまま達成率へ変換しません。" \
  "目標を設定したことと、成果を上げたことは別です。"
check_content "/policies/fukuoka-prefecture/initiatives/02/" \
  "世界から選ばれる福岡県の実現" \
  "企業立地件数" \
  "県及び市町村による産業用地の整備着手面積" \
  "福岡空港の新規国際路線誘致数" \
  "当初値は公式資料でダッシュ表記です。0とは扱わず"
check_content "/policies/fukuoka-prefecture/initiatives/03/" \
  "ワンヘルスの推進" \
  "ワンヘルス宣言事業者登録数" \
  "11,000件" \
  "当初値は公式資料でダッシュ表記です。0とは扱わず"
check_content "/policies/fukuoka-prefecture/initiatives/04/" \
  "移住定住の促進" \
  "県外からの移住世帯数" \
  "ふくおかファンクラブ会員数" \
  "5,000世帯"
check_content "/policies/fukuoka-prefecture/initiatives/05/" \
  "デジタル社会の実現" \
  "国が示すオンライン化を推進すべき手続のオンライン化達成率" \
  "中小企業におけるDXの実践割合" \
  "全国参考値"
check_content "/policies/fukuoka-prefecture/initiatives/06/" \
  "グリーン社会の実現" \
  "温室効果ガスの総排出量の削減率" \
  "再生可能エネルギー発電設備導入容量" \
  "405万kW"
check_content "/policies/fukuoka-prefecture/initiatives/07/" \
  "成長産業の創出" \
  "成長産業分野への新規参画企業数" \
  "1億円以上の資金調達を行ったベンチャー企業数" \
  "80社"
check_content "/policy-sources/" \
  "集められる政策資料から、先に形にする。" \
  "計画から支出と成果まで、順番につなぐ。" \
  "公開されている深さを、自治体ごとに分けて見る。" \
  "計画の基本方向" \
  "取組別の進捗" \
  "重点事業シート" \
  "入口確認のみ" \
  "資料10件を登録しましたが、政策評価はまだ0件です。"
printf '\nResult: PASS\n' >> "$REPORT"
cat "$REPORT"
