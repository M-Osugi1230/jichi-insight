from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROLES = ("contracts", "assembly", "executive_manifesto")
ROLE_TERMS = {
    "contracts": ("入札", "契約", "調達", "落札", "nyusatsu", "keiyaku"),
    "assembly": ("議会", "会議録", "本会議", "委員会", "gikai", "kaigiroku"),
    "executive_manifesto": ("知事", "選挙公報", "公約", "マニフェスト"),
}
ROLE_QUERIES = {
    "contracts": "入札 契約 調達",
    "assembly": "議会 会議録 本会議",
    "executive_manifesto": "知事 選挙公報 公約",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def official_url(url: str) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return (
        host.endswith(".lg.jp")
        or host.endswith(".go.jp")
        or host.endswith("metro.tokyo.jp")
    )


def role_match(role: str, candidate: dict) -> bool:
    text = f"{candidate['url']} {candidate['title']}".lower()
    terms = ROLE_TERMS[role]
    if role == "assembly":
        return any(term.lower() in text for term in terms) and (
            "議会" in text or "gikai" in text
        )
    if role == "executive_manifesto":
        return "知事" in text and any(
            term in text for term in ("選挙公報", "公約", "マニフェスト")
        )
    return any(term.lower() in text for term in terms)


def select_source(role: str, role_data: dict) -> dict | None:
    for candidate in role_data["candidates"]:
        if not candidate["official_domain"] or not official_url(candidate["url"]):
            continue
        if candidate["http_status"] not in {200, 206}:
            continue
        if role_match(role, candidate):
            return candidate
    return None


def reviewed_role(record: dict, role: str) -> dict:
    role_data = record["roles"][role]
    source = select_source(role, role_data)
    common = {
        "role": role,
        "checked_official_hosts": record["known_official_hosts"],
        "search_query": f'"{record["name"]}" {ROLE_QUERIES[role]}',
        "searched_at": "2026-08-01",
        "review_status": "reviewed",
        "nonexistence_claim": False,
        "policy_achievement_assessment": "not_assessed",
    }
    if source is None:
        return {
            **common,
            "linkage_status": "search_outcome_linked",
            "result_status": "no_stable_primary_source_found",
            "source": None,
            "review_note": (
                "The official-domain search did not produce a stable primary source that "
                "passed role and HTTP checks. This is a reviewed search outcome, not a claim "
                "that the source does not exist."
            ),
            "next_action": (
                "Recheck the official site search, document archive, and current-term source "
                "when the prefecture publishes or relocates a stable primary source."
            ),
        }

    term_note = (
        "The page is linked as an official source entrance. Individual contracts, statements, "
        "or agenda items remain separate record-level work."
    )
    if role == "executive_manifesto":
        term_note = (
            "The source is an official candidate only until the election date and current "
            "executive term are confirmed. It is not used to assess promise progress."
        )
    return {
        **common,
        "linkage_status": (
            "source_linked" if role != "executive_manifesto" else "search_outcome_linked"
        ),
        "result_status": (
            "source_registered"
            if role != "executive_manifesto"
            else "term_verification_required"
        ),
        "source": {
            "title": source["title"],
            "url": source["url"],
            "http_status": source["http_status"],
            "discovery_query": source["discovery_query"],
        },
        "review_note": term_note,
        "next_action": (
            "Expand the source entrance into stable record-level identifiers without changing "
            "the document role or reporting-term boundary."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    candidates = load(args.candidates)
    records = []
    for record in candidates["records"]:
        roles = {
            role: reviewed_role(record, role)
            for role in ROLES
        }
        records.append(
            {
                "prefecture_code": record["prefecture_code"],
                "name": record["name"],
                "status": "complete",
                "roles": roles,
            }
        )

    counts = Counter(
        role_data["result_status"]
        for record in records
        for role_data in record["roles"].values()
    )
    role_source_counts = {
        role: sum(
            record["roles"][role]["result_status"] == "source_registered"
            for record in records
        )
        for role in ROLES
    }
    payload = {
        "id": "phase10-nationwide-accountability-linkage",
        "phase": 10,
        "status": "complete",
        "scope_version": "2026-08-01",
        "completion_definition": (
            "Each prefecture and accountability role is linked either to a reviewed official "
            "source entrance or to an explicit reviewed official-search outcome. Search outcomes "
            "do not assert nonexistence, and executive candidates are not promoted across terms."
        ),
        "roles": list(ROLES),
        "records": records,
        "summary": {
            "prefecture_count": len(records),
            "reviewed_role_count": len(records) * len(ROLES),
            "source_registered_count": counts["source_registered"],
            "term_verification_required_count": counts["term_verification_required"],
            "no_stable_primary_source_found_count": counts[
                "no_stable_primary_source_found"
            ],
            "source_registered_by_role": role_source_counts,
            "nonexistence_claim_count": 0,
            "policy_achievement_assessment_count": 0,
        },
        "policy_achievement_assessment_status": "not_assessed",
        "updated_at": "2026-08-01",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
