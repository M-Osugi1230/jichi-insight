from __future__ import annotations

import argparse
import json
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
        "query": "入札 契約 調達 電子調達",
        "positive": ("入札", "契約", "調達", "落札", "nyusatsu", "keiyaku", "procurement", "bid"),
        "negative": ("採用", "試験", "統計"),
    },
    "assembly": {
        "query": "県議会 会議録 本会議 委員会",
        "positive": ("議会", "会議録", "本会議", "委員会", "gikai", "kaigiroku", "assembly"),
        "negative": ("市議会", "町議会", "村議会"),
    },
    "executive_manifesto": {
        "query": "知事 選挙公報 公約 マニフェスト",
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
    return (
        normalized.endswith(".lg.jp")
        or normalized.endswith(".go.jp")
        or normalized.endswith("metro.tokyo.jp")
    )


def source_hosts_by_prefecture() -> dict[str, set[str]]:
    hosts = {code: set() for code in PREFECTURES}
    for relative in REVIEW_FILES:
        payload = load_json(ROOT / relative)
        for record in payload.get("records", []):
            code = record["prefecture_code"]
            direct_url = record.get("url")
            if direct_url:
                host = normalize_host(urlparse(direct_url).netloc)
                if host:
                    hosts[code].add(host)
            for source in record.get("sources", {}).values():
                host = normalize_host(urlparse(source["url"]).netloc)
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


def search_duckduckgo(query: str, limit: int = 10) -> list[tuple[str, str]]:
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    response = SESSION.get(url, timeout=20)
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


def verify_url(url: str) -> tuple[str, int | None]:
    try:
        response = SESSION.get(
            url,
            timeout=12,
            allow_redirects=True,
            headers={"Range": "bytes=0-200000"},
        )
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
    soup = BeautifulSoup(response.text[:200_000], "html.parser")
    if soup.title:
        return " ".join(soup.title.get_text(" ", strip=True).split()), status
    return "", status


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
    is_official = official_host(host) or any(
        host == known or host.endswith(f".{known}") for known in known_hosts
    )
    score = 8 if is_official else 0
    short_name = prefecture_name.removesuffix("県").removesuffix("府").removesuffix("都")
    if short_name.lower() in text:
        score += 2
    score += sum(3 for keyword in config["positive"] if keyword.lower() in text)
    score -= sum(5 for keyword in config["negative"] if keyword.lower() in text)
    if role == "executive_manifesto" and "選挙公報" in text:
        score += 6
    if role == "assembly" and "会議録" in text:
        score += 5
    if role == "contracts" and any(word in text for word in ("入札", "調達", "落札")):
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
    prefecture_name: str,
    role: str,
    known_hosts: set[str],
) -> list[Candidate]:
    config = ROLE_CONFIG[role]
    preferred_host = sorted(known_hosts)[0] if known_hosts else None
    query = f'"{prefecture_name}" {config["query"]}'
    if preferred_host:
        query = f"site:{preferred_host} {config['query']}"
    try:
        results = search_duckduckgo(query)
    except requests.RequestException:
        results = []

    ranked: list[Candidate] = []
    for url, title in results:
        host = normalize_host(urlparse(url).netloc)
        if not host or not official_host(host):
            continue
        score, is_official = score_candidate(
            url=url,
            title=title,
            role=role,
            prefecture_name=prefecture_name,
            known_hosts=known_hosts,
        )
        ranked.append(
            Candidate(
                url=url,
                title=title,
                score=score,
                source=query,
                http_status=None,
                official_domain=is_official,
            )
        )

    verified: list[Candidate] = []
    for candidate in dedupe(ranked)[:3]:
        fetched_title, status = verify_url(candidate.url)
        title = fetched_title or candidate.title
        score, is_official = score_candidate(
            url=candidate.url,
            title=title,
            role=role,
            prefecture_name=prefecture_name,
            known_hosts=known_hosts,
        )
        verified.append(
            Candidate(
                url=candidate.url,
                title=title,
                score=score,
                source=query,
                http_status=status,
                official_domain=is_official,
            )
        )
    time.sleep(0.05)
    return [candidate for candidate in dedupe(verified) if candidate.score >= 10][:3]


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
            "Candidates must be reviewed for prefecture, source role, reporting period, "
            "and current executive term before promotion."
        ),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = ["# Phase 10 accountability source discovery", ""]
    for record in records:
        lines.append(f"## {record['prefecture_code']} {record['name']}")
        for role, role_data in record["roles"].items():
            lines.append(
                f"- {role}: {role_data['status']} "
                f"({len(role_data['candidates'])})"
            )
            for candidate in role_data["candidates"]:
                lines.append(
                    f"  - {candidate['score']} {candidate['title']} — "
                    f"{candidate['url']}"
                )
        lines.append("")
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
