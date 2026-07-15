#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${JICHI_PRODUCTION_URL:-https://m-osugi1230.github.io/jichi-insight}"
REPORT="${JICHI_SMOKE_REPORT:-production-smoke-report.txt}"
INDEX_FILE="$(mktemp)"
trap 'rm -f "$INDEX_FILE"' EXIT

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
  "/methodology/"
  "/municipalities/"
  "/municipalities/fukuoka-prefecture/"
  "/municipalities/fukuoka-city/"
  "/municipalities/kitakyushu-city/"
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

printf '\nResult: PASS\n' >> "$REPORT"
cat "$REPORT"
