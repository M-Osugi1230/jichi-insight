from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

PREFECTURES = {
    f"{index:02d}": name
    for index, name in enumerate(
        [
            "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
            "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
            "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
            "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
            "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
            "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
            "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
        ],
        start=1,
    )
}

REVIEW_FILES = [
    "data/catalog/phase10_reference_depth_reviews.json",
    "data/catalog/phase10_anchor_depth_reviews.json",
    "data/catalog/phase10_tohoku_depth_reviews.json",
    "data/catalog/phase10_kanto_depth_reviews.json",
    "data/catalog/phase10_chubu_depth_reviews.json",
    "data/catalog/phase10_kinki_depth_reviews.json",
    "data/catalog/phase10_chugoku_depth_reviews.json",
    "data/catalog/phase10_shikoku_depth_reviews.json",
    "data/catalog/phase10_kyushu_depth_reviews.json",
]

ROLE_CONFIG = {
    "contracts": {
        "query_terms": ("入札 契約 調達", "電子調達 入札情報"),
        "positive": ("入札", "契約", "調達", "落札", "nyusatsu", "keiyaku", "procurement", "bid"),
        "negative": ("採用", "試験", "統計"),
    },
    "assembly": {
        "query_terms": ("県議会 会議録", "議会 本会議 会議録"),
        "positive": ("議会", "会議録", "本会議", "委員会", "gikai", "kaigiroku", "assembly"),
        "negative": ("市議会", "町議会", "村議会"),
    },
    "executive_manifesto": {
        "query_terms": ("知事 選挙公報 公約", "知事 マニフェスト 公約"),
        "positive": ("知事", "選挙公報", "公約", "マニフェスト", "senkyo", "kouhou", "manifesto"),
        "negative": ("市長", "町長", "村長", "議員"),
    },
}

USER_AGENT = "JichiInsightPhase10SourceDiscovery/1.0 (+https://github.com/M-Osugi1230/jichi-insight)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "ja,en;q=0.5"})


@dataclass(frozen=True)
class Candidate:
    url: str
    title: str
    score: int
    source: str
    http_status: int | None
    official_domain: bool


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_host(host: str) -> str:
    return host.lower().split(":", 1)[0].removeprefix("www.")


def official_host(host: str) -> bool:
    normalized = normalize_host(host)
    return normalized.endswith(".lg.jp") or normalized.endswith(".go.jp") or normalized.endswith("metro.tokyo.jp")


def source_hosts_by_prefecture() -> dict[str, set[str]]:
    hosts = {code: set() for code in PREFECTURES}
    for relative in REVIEW_FILES:
        payload = load_json(ROOT / relative)
        for record in payload.get("records", []):
            code = record["prefecture_code"]
            for source in record.get("sources", {}).values():
                host = normalize_host(urlparse(source["url"]).netloc)
                if host:
                    hosts[code].add(host)
        for review in payload.get("reviews", []):
            code = review["prefecture_code"]
            host = normalize_host(urlparse(review["url"]).netloc)
            if host:
                hosts[code].add(host)
    return hosts


def unwrap_search_url(url: str) -> str:
    parsed = urlparse(url)
    if "duckduckgo.com" in parsed.netloc:
        query = parse_qs(parsed.query)
        if "uddg" in query:
            return unquote(query["uddg"][0])
    return url


def search_duckduckgo(query: str, limit: int = 12) -> list[tuple[str, str]]:
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    response = SESSION.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results: list[tuple[str, str]] = []
    for anchor in soup.select("a.result__a"):
        href = unwrap_search_url(anchor.get("href", ""))
        title = " ".join(anchor.get_text(" ", strip=True).split())
        if href.startswith("http") and title:
            results.append((href, title))
        if len(results) >= limit:
            break
    return results


def page_title(url: str) -> tuple[str, int | None]:
    try:
        response = SESSION.get(url, timeout=25, allow_redirects=True)
    except requests.RequestException:
        return "", None
    status = response.status_code
    if status >= 400:
        return "", status
    content_type = response.headers.get("content-type", "")
    if "pdf" in content_type.lower() or response.url.lower().endswith(".pdf"):
        return Path(urlparse(response.url).path).name, status
    if "html" not in content_type.lower() and not response.text.lstrip().startswith("<"):
        return "", status
    soup = BeautifulSoup(response.text[:1_500_000], "html.parser")
    title = ""
    if soup.title:
        title = " ".join(soup.title.get_text(" ", strip=True).split())
    if not title:
        heading = soup.find(["h1", "h2"])
        if heading:
            title = " ".join(heading.get_text(" ", strip=True).split())
    return title, status


def score_candidate(
    *,
    url: str,
    title: str,
    role: str,
    prefecture_name: str,
    known_hosts: set[str],
) -> tuple[int, bool]:
    config = ROLE_CONFIG[role]
    text = f"{unquote(url)} {title}".lower()
    host = normalize_host(urlparse(url).netloc)
    is_official = official_host(host) or any(host == known or host.endswith(f".{known}") for known in known_hosts)
    score = 0
    if is_official:
        score += 8
    if prefecture_name.replace("県", "").replace("府", "").replace("都", "").lower() in text:
        score += 2
    for keyword in config["positive"]:
        if keyword.lower() in text:
            score += 3
    for keyword in config["negative"]:
        if keyword.lower() in text:
            score -= 5
    if role == "executive_manifesto" and ("選挙公報" in text or "manifesto" in text):
        score += 6
    if role == "assembly" and ("会議録" in text or "kaigiroku" in text):
        score += 5
    if role == "contracts" and ("入札" in text or "調達" in text or "落札" in text):
        score += 4
    return score, is_official


def dedupe(values: Iterable[Candidate]) -> list[Candidate]:
    best: dict[str, Candidate] = {}
    for candidate in values:
        key = candidate.url.rstrip("/")
        previous = best.get(key)
        if previous is None or candidate.score > previous.score:
            best[key] = candidate
    return sorted(best.values(), key=lambda item: (-item.score, item.url))


def discover_role(
    *,
    code: str,
    prefecture_name: str,
    role: str,
    known_hosts: set[str],
) -> list[Candidate]:
    config = ROLE_CONFIG[role]
    queries = []
    for terms in config["query_terms"]:
        queries.append(f'"{prefecture_name}" {terms}')
        for host in sorted(known_hosts)[:2]:
            queries.append(f"site:{host} {terms}")
    candidates: list[Candidate] = []
    for query in queries:
        try:
            results = search_duckduckgo(query)
        except requests.RequestException:
            continue
        for url, search_title in results:
            host = normalize_host(urlparse(url).netloc)
            if not host or not official_host(host):
                continue
            fetched_title, status = page_title(url)
            title = fetched_title or search_title
            score, is_official = score_candidate(
                url=url,
                title=title,
                role=role,
                prefecture_name=prefecture_name,
                known_hosts=known_hosts,
            )
            candidates.append(
                Candidate(
                    url=url,
                    title=title,
                    score=score,
                    source=query,
                    http_status=status,
                    official_domain=is_official,
                )
            )
            time.sleep(0.05)
        time.sleep(0.15)
    return [candidate for candidate in dedupe(candidates) if candidate.score >= 10][:5]


def serialize(candidate: Candidate) -> dict:
    return {
        "url": candidate.url,
        "title": candidate.title,
        "score": candidate.score,
        "discovery_query": candidate.source,
        "http_status": candidate.http_status,
        "official_domain": candidate.official_domain,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--codes", nargs="*", default=list(PREFECTURES))
    args = parser.parse_args()

    hosts_by_code = source_hosts_by_prefecture()
    records = []
    for code in args.codes:
        name = PREFECTURES[code]
        roles = {}
        for role in ROLE_CONFIG:
            candidates = discover_role(
                code=code,
                prefecture_name=name,
                role=role,
                known_hosts=hosts_by_code[code],
            )
            roles[role] = {
                "status": "candidate_found" if candidates else "not_found",
                "candidates": [serialize(candidate) for candidate in candidates],
            }
        records.append(
            {
                "prefecture_code": code,
                "name": name,
                "known_official_hosts": sorted(hosts_by_code[code]),
                "roles": roles,
            }
        )

    payload = {
        "id": "phase10-accountability-source-candidates",
        "status": "candidate_only",
        "review_rule": (
            "Candidates must be manually reviewed for prefecture, source role, reporting period, "
            "and current executive term before promotion."
        ),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = ["# Phase 10 accountability source discovery", ""]
    for record in records:
        lines.append(f"## {record['prefecture_code']} {record['name']}")
        for role, role_data in record["roles"].items():
            lines.append(f"- {role}: {role_data['status']} ({len(role_data['candidates'])})")
            for candidate in role_data["candidates"][:3]:
                lines.append(f"  - {candidate['score']} {candidate['title']} — {candidate['url']}")
        lines.append("")
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
