"""
AI Overview Rewrite Queue API: A Quick Start Example
See more at: https://apify.com/johnvc/ai-overview-rewrite-queue?fpr=9n7kx3
Input schema: https://apify.com/johnvc/ai-overview-rewrite-queue/input-schema?fpr=9n7kx3

This script shows how to call the AI Overview Rewrite Queue API on Apify from
Python and read its structured JSON output. It is an "ai overview tracking"
pipeline: give it your domains plus a Google Search Console Queries export
(or a queries list), and it returns one row per query that joins the Search
Console fields (clicks, impressions, ctr, position) to live AI Overview
citation fields, plus a tier (A through X), a tier_reason, and a join_status.

This is a composition Actor. The citation half runs the sibling Actor
johnvc/google-ai-overview-api. Because a single run charges YOUR Apify account
for BOTH this Actor's events AND the child citation Actor's events, every
example here checks only 2 to 3 queries so your first run stays inexpensive.
Raise the input sizes once you know your budget.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3

Examples:
  uv run python ai-overview-rewrite-queue-api-example.py
  uv run python ai-overview-rewrite-queue-api-example.py --example default
  uv run python ai-overview-rewrite-queue-api-example.py --example find-pages-to-rewrite-first
  uv run python ai-overview-rewrite-queue-api-example.py --example join-search-console
  uv run python ai-overview-rewrite-queue-api-example.py --example find-top4-never-cited
"""

from __future__ import annotations

import argparse
import os
from typing import Any

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = "johnvc/ai-overview-rewrite-queue"


def _run_and_collect(client: ApifyClient, run_input: dict[str, Any]) -> list[dict[str, Any]]:
    """Call the Actor and return the rows from its default dataset."""
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    if run is None:
        raise SystemExit("The Actor run did not return a result.")
    return list(client.dataset(run.default_dataset_id).iterate_items())


def _print_rows(items: list[dict[str, Any]]) -> None:
    """Print a short, readable summary of the scored rows.

    Args:
        items: Rows returned from the Actor's default dataset.
    """
    scored = [row for row in items if row.get("result_type") == "scored_query"]
    errors = [row for row in items if row.get("result_type") == "error"]

    print(f"Returned {len(items)} row(s): {len(scored)} scored, {len(errors)} error.\n")

    for row in scored:
        # A few of the most useful fields from each scored row.
        print(f"[{row.get('tier')}] {row.get('query')}")
        print(f"    position={row.get('position')} impressions={row.get('impressions')} "
              f"clicks={row.get('clicks')}")
        print(f"    citation_state={row.get('citation_state')} "
              f"ai_overview_present={row.get('ai_overview_present')} "
              f"join_status={row.get('join_status')}")
        print(f"    why: {row.get('tier_reason')}")
        print()

    for row in errors:
        # error rows carry error_type + error_message instead of scores.
        print(f"[error:{row.get('error_type')}] {row.get('error_message')}")


def run_default(client: ApifyClient) -> None:
    """Cheap general quick-start that exercises most input parameters."""
    # Inputs are kept small (a single domain and only 3 queries total) to keep
    # this first run inexpensive. This Actor bills your account for its own
    # events AND for the child citation Actor's events, so every extra query is
    # two charges, not one. Raise these once you know your budget.
    run_input: dict[str, Any] = {
        "target_domains": ["example.com"],
        "search_console_rows": [
            {"query": "what is a crm", "clicks": 12, "impressions": 1900, "ctr": "0.63%", "position": 8.4},
            {"query": "crm pricing guide", "clicks": 40, "impressions": 2600, "ctr": "1.54%", "position": 3.1},
        ],
        "queries": ["best crm for small business"],
        "min_impressions": 5,
        "gl": "us",
        "hl": "en",
    }
    items = _run_and_collect(client, run_input)
    _print_rows(items)


def run_find_pages_to_rewrite_first(client: ApifyClient) -> None:
    """Mirrors Store task: Find which pages to rewrite first for AI Overviews.

    https://apify.com/johnvc/ai-overview-rewrite-queue/examples/find-which-pages-to-rewrite-first-for-ai-overviews?fpr=9n7kx3

    Send your domains plus a Search Console export, then read the Tier A rows:
    queries where you rank 5 to 20 and a competitor is cited in the AI Overview
    instead of you. Those are the highest-leverage pages to rewrite first.
    """
    # Kept to 2 queries on purpose: each query is billed on this Actor AND the
    # child citation Actor, so a small export keeps the first run cheap.
    run_input: dict[str, Any] = {
        "target_domains": ["example.com"],
        "search_console_rows": [
            {"query": "what is a crm", "clicks": 12, "impressions": 1900, "ctr": "0.63%", "position": 8.4},
            {"query": "crm pricing guide", "clicks": 40, "impressions": 2600, "ctr": "1.54%", "position": 3.1},
        ],
        "min_impressions": 5,
        "gl": "us",
        "hl": "en",
    }
    items = _run_and_collect(client, run_input)

    tier_a = [r for r in items if r.get("result_type") == "scored_query" and r.get("tier") == "A"]
    print(f"Tier A (rewrite these first): {len(tier_a)} of {len(items)} row(s).\n")
    _print_rows(items)


def run_join_search_console(client: ApifyClient) -> None:
    """Mirrors Store task: Join a Search Console export with AI Overview data.

    https://apify.com/johnvc/ai-overview-rewrite-queue/examples/join-a-search-console-export-with-ai-overview-data?fpr=9n7kx3

    One JSON row per query, with the Search Console fields (clicks, impressions,
    ctr, position) joined to the live citation fields (citation_state,
    reference_domains, cited_urls). join_status tells you which side each query
    came from. To pull from a live export instead of pasted rows, set
    search_console_csv_url to a published Google Sheet CSV.
    """
    # 2 rows only, to keep the paired billing small on this first run.
    run_input: dict[str, Any] = {
        "target_domains": ["example.com"],
        "search_console_rows": [
            {"query": "what is a crm", "clicks": 12, "impressions": 1900, "ctr": "0.63%", "position": 8.4},
            {"query": "best free crm", "clicks": 88, "impressions": 4200, "ctr": "2.10%", "position": 2.4},
        ],
        "min_impressions": 5,
        "gl": "us",
        "hl": "en",
        # "search_console_csv_url": "https://docs.google.com/.../pub?output=csv",
    }
    items = _run_and_collect(client, run_input)

    print("Joined rows (Search Console fields + AI Overview citation fields):\n")
    for row in items:
        if row.get("result_type") != "scored_query":
            continue
        print(f"{row.get('query')}  ->  join_status={row.get('join_status')}")
        print(f"    clicks={row.get('clicks')} impressions={row.get('impressions')} "
              f"ctr={row.get('ctr')} position={row.get('position')}")
        print(f"    citation_state={row.get('citation_state')} "
              f"reference_domains={row.get('reference_domains')} "
              f"cited_urls={row.get('cited_urls')}")
        print()


def run_find_top4_never_cited(client: ApifyClient) -> None:
    """Mirrors Store task: Find pages that rank top 4 but are never cited by AI.

    https://apify.com/johnvc/ai-overview-rewrite-queue/examples/find-pages-that-rank-top-4-but-are-never-cited-by-ai?fpr=9n7kx3

    Read the Tier B rows: queries where you already rank in the top four and the
    AI Overview still ignores you. That is an answer-shape problem no ranking
    report will surface.
    """
    # 2 top-ranking queries, kept small to keep the paired billing cheap.
    run_input: dict[str, Any] = {
        "target_domains": ["example.com"],
        "search_console_rows": [
            {"query": "crm pricing guide", "clicks": 40, "impressions": 2600, "ctr": "1.54%", "position": 3.1},
            {"query": "best free crm", "clicks": 88, "impressions": 4200, "ctr": "2.10%", "position": 2.4},
        ],
        "min_impressions": 5,
        "gl": "us",
        "hl": "en",
    }
    items = _run_and_collect(client, run_input)

    tier_b = [r for r in items if r.get("result_type") == "scored_query" and r.get("tier") == "B"]
    print(f"Tier B (rank top 4, ignored by the AI Overview): {len(tier_b)} of {len(items)} row(s).\n")
    _print_rows(items)


def main() -> None:
    """Dispatch a quick-start or a task-aligned recipe."""
    parser = argparse.ArgumentParser(description="AI Overview Rewrite Queue API examples")
    parser.add_argument(
        "--example",
        default="default",
        choices=[
            "default",
            "find-pages-to-rewrite-first",
            "join-search-console",
            "find-top4-never-cited",
        ],
        help="Which recipe to run (see the README Recipes section).",
    )
    args = parser.parse_args()

    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise SystemExit("Set APIFY_API_TOKEN in .env or the environment.")

    client = ApifyClient(token)
    dispatch = {
        "default": run_default,
        "find-pages-to-rewrite-first": run_find_pages_to_rewrite_first,
        "join-search-console": run_join_search_console,
        "find-top4-never-cited": run_find_top4_never_cited,
    }
    dispatch[args.example](client)


if __name__ == "__main__":
    main()
