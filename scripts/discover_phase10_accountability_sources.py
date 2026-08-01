from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
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
        "query": "入札 契約 調達",
        "positive": ("入札", "契約", "調達", "落札", "nyusatsu", "keiyaku"),
        "negative": ("採用", "試験"),
    },
    "assembly": {
        "query": "議会 会議録 本会議",
        "positive": ("議会", "会議録", "本会議", "委員会", "gikai", "kaigiroku"),
        "negative": ("市議会", "町議会", "村議会"),
    },
    "executive_manifesto": {
        "query": "知事 選挙公報 公約",
        "positive": ("知事", "選挙公報", "公約", "マニフェスト", "senkyo", "kouhou"),
        "negative": ("市長", "町長", "村長", "議員"),
    },
}
HEADERS = {
    "User-Agent": (
        "JichiInsightPhase10SourceDiscovery/1.3 "
        "(+https://github.com/M-Osugi1230/jichi-insight)"
    ),
    "Accept-Language": "ja,en;q=0.5",
}
LOCAL_GOVERNMENT_HOST_MARKERS = (
    ".city.",
    ".town.",
    ".vill.",
    ".village.",
    "city.",
    "town.",
    "vill.",
)


@dataclass(frozen=True)
class Candidate:
    url: str
    title: str
    score: int
    discovery_query: str
    http_status: int | None
    official_domain: bool
    prefecture_host_match: bool


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def host(url: str) -> str:
    return urlparse(url).netloc.lower().split(":", 1)[0].removeprefix("www.")


def is_official(url: str) -> bool:
    value = host(url)
    return (
        value.endswith(".lg.jp")
        or value.endswith(".go.jp")
        or value.endswith("metro.tokyo.jp")
    )


def matches_prefecture_host(url: str, official_hosts: set[str]) -> bool:
    value = host(url)
    if any(marker in value for marker in LOCAL_GOVERNMENT_HOST_MARKERS):
        return False
    return any(value == known or value.endswith(f".{known}") for known in official_hosts)


def known_hosts() -> dict[str, set[str]]:
    result = {code: set() for code in PREFECTURES}
    for relative in REVIEW_FILES:
        for record in load(ROOT / relative)["records"]:
            code = record["prefecture_code"]
            urls = [record.get("url")]
            urls.extend(
                source.get("url")
                for source in record.get("sources", {}).values()
            )
            result[code].update(host(url) for url in urls if url)
    return result


def unwrap(url: str) -> str:
    parsed = urlparse(url)
    if "duckduckgo.com" in parsed.netloc:
        values = parse_qs(parsed.query).get("uddg")
        if values:
            return unquote(values[0])
    return url


def search(query: str, limit: int = 12) -> list[tuple[str, str]]:
    response = requests.get(
        f"https://html.duckduckgo.com/html/?q={quote_plus(query)}",
        timeout=20,
        headers=HEADERS,
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    output = []
    for anchor in soup.select("a.result__a"):
        url = unwrap(anchor.get("href", ""))
        title = " ".join(anchor.get_text(" ", strip=True).split())
        if url.startswith("http") and title:
            output.append((url, title))
        if len(output) >= limit:
            break
    return output


def score(url: str, title: str, prefecture: str, role: str) -> int:
    config = ROLE_CONFIG[role]
    text = f"{unquote(url)} {title}".lower()
    short_name = prefecture.removesuffix("県").removesuffix("府").removesuffix("都")
    value = 8 if is_official(url) else 0
    value += 2 if short_name.lower() in text else 0
    value += sum(3 for word in config["positive"] if word.lower() in text)
    value -= sum(5 for word in config["negative"] if word.lower() in text)
    if role == "contracts" and any(word in text for word in ("入札", "調達", "落札")):
        value += 4
    if role == "assembly" and "会議録" in text:
        value += 5
    if role == "executive_manifesto" and "選挙公報" in text:
        value += 6
    return value


def verify(url: str) -> tuple[str, int | None]:
    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            headers={**HEADERS, "Range": "bytes=0-150000"},
        )
    except requests.RequestException:
        return "", None
    if response.status_code >= 400:
        return "", response.status_code
    content_type = response.headers.get("content-type", "").lower()
    if "pdf" in content_type or response.url.lower().endswith(".pdf"):
        return Path(urlparse(response.url).path).name, response.status_code
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text[:150_000], "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    return " ".join(title.split()), response.status_code


def ranked_results(
    prefecture: str,
    role: str,
    official_hosts: set[str],
) -> list[Candidate]:
    config = ROLE_CONFIG[role]
    queries = [f'"{prefecture}" {config["query"]}']
    if official_hosts:
        queries.append(f"site:{sorted(official_hosts)[0]} {config['query']}")

    raw: dict[str, tuple[str, str]] = {}
    for query in queries:
        try:
            for url, title in search(query):
                if is_official(url) and matches_prefecture_host(url, official_hosts):
                    raw.setdefault(url.rstrip("/"), (title, query))
        except requests.RequestException:
            continue
        if raw:
            break

    preliminary = sorted(
        (
            (score(url, title, prefecture, role), url, title, query)
            for url, (title, query) in raw.items()
        ),
        reverse=True,
    )[:4]
    candidates = []
    for _, url, search_title, query in preliminary:
        fetched_title, status = verify(url)
        title = fetched_title or search_title
        final_score = score(url, title, prefecture, role)
        if final_score >= 10:
            candidates.append(
                Candidate(
                    url=url,
                    title=title,
                    score=final_score,
                    discovery_query=query,
                    http_status=status,
                    official_domain=True,
                    prefecture_host_match=True,
                )
            )
    return sorted(candidates, key=lambda item: (-item.score, item.url))[:3]


def discover_task(
    code: str,
    role: str,
    official_hosts: dict[str, set[str]],
) -> tuple[str, str, list[Candidate]]:
    return code, role, ranked_results(PREFECTURES[code], role, official_hosts[code])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--codes", nargs="*", default=list(PREFECTURES))
    args = parser.parse_args()

    official_hosts = known_hosts()
    results: dict[tuple[str, str], list[Candidate]] = {}
    tasks = [(code, role) for code in args.codes for role in ROLE_CONFIG]
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(discover_task, code, role, official_hosts): (code, role)
            for code, role in tasks
        }
        for future in as_completed(futures):
            code, role = futures[future]
            try:
                _, _, candidates = future.result()
            except Exception:
                candidates = []
            results[(code, role)] = candidates

    records = []
    for code in args.codes:
        roles = {}
        for role in ROLE_CONFIG:
            candidates = results[(code, role)]
            roles[role] = {
                "status": "candidate_found" if candidates else "not_found",
                "candidates": [asdict(item) for item in candidates],
            }
        records.append(
            {
                "prefecture_code": code,
                "name": PREFECTURES[code],
                "known_official_hosts": sorted(official_hosts[code]),
                "roles": roles,
            }
        )

    payload = {
        "id": "phase10-accountability-source-candidates",
        "status": "candidate_only",
        "review_rule": (
            "Candidates require exact prefecture-host, source-role, reporting-period, and "
            "current executive-term review before registration. A missing result is not an "
            "assertion that a source does not exist."
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
                f"- {role}: {role_data['status']} ({len(role_data['candidates'])})"
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
