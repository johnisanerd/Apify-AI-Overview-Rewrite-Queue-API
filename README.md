# 🔎 AI Overview Rewrite Queue API: ai overview tracking that ranks which pages to rewrite first

> Join your Google Search Console export to live AI Overview citation data and get back a scored, tiered rewrite queue: the pages losing clicks to Google's AI, highest-leverage first, each with a plain reason.

**Actor page:** [apify.com/johnvc/ai-overview-rewrite-queue](https://apify.com/johnvc/ai-overview-rewrite-queue?fpr=9n7kx3)
**Input schema:** [apify.com/johnvc/ai-overview-rewrite-queue/input-schema](https://apify.com/johnvc/ai-overview-rewrite-queue/input-schema?fpr=9n7kx3)

The AI Overview Rewrite Queue API turns ai overview tracking into a work list. Give it the domains you own and a Search Console Queries export, and it returns one structured JSON row per query. Each row joins your Search Console fields (clicks, impressions, ctr, position) to live AI Overview citation fields (whether an AI Overview appeared, who it cited, whether any of your pages made the reference list), then scores the query into a tier from A to X with a one-sentence reason. It is a practical AI visibility instrument: instead of a raw citation tracking dump, you get a ranked queue that tells you where a rewrite will move the needle.

## Video Walkthrough

[![Watch the walkthrough](https://img.youtube.com/vi/jREWahDGhJM/maxresdefault.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

### Text walkthrough

This repo teaches ai overview tracking with the AI Overview Rewrite Queue API on Apify. The main input is your `target_domains` plus a Google Search Console Queries export, passed either as a published CSV URL (`search_console_csv_url`) or as pasted rows (`search_console_rows`); you can add extra `queries` to check on top of the export. For every query it returns a `tier` (A through X) and a `tier_reason`, next to the joined citation fields: `citation_state`, `ai_overview_present`, `reference_domains`, `cited_urls`, and `join_status`. The highest-value use case is Tier A: queries where you rank 5 to 20 and a competitor is cited in the AI Overview instead of you, which is exactly the set of pages worth rewriting first (see the "Find which pages to rewrite first for AI Overviews" recipe below). Tier B flags the opposite blind spot, pages that rank in the top four yet the AI ignores, an answer-shape problem a normal ranking report never shows. The citation half of every run is handled by the sibling Actor `johnvc/google-ai-overview-api`, and a run summary is written to the key-value store. Because it joins two datasets you already care about, it reads less like a dashboard and more like a to-do list ordered by lost opportunity.

## Quick Start

### Prerequisites
- Python 3.11 or higher
- An Apify account and API key ([get a free key here](https://apify.com?fpr=9n7kx3))

1. **Clone the repository**
   ```bash
   git clone https://github.com/johnisanerd/Apify-AI-Overview-Rewrite-Queue-API.git
   cd Apify-AI-Overview-Rewrite-Queue-API
   ```

2. **Install dependencies with UV**
   ```bash
   # Install UV if you do not have it:
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install project dependencies:
   uv sync
   ```

3. **Configure your API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your Apify API key
   # Get your free API key at: https://apify.com?fpr=9n7kx3
   ```

4. **Run the example**
   ```bash
   uv run python ai-overview-rewrite-queue-api-example.py
   # Optional recipes (see the Recipes section):
   # uv run python ai-overview-rewrite-queue-api-example.py --example find-pages-to-rewrite-first
   # uv run python ai-overview-rewrite-queue-api-example.py --example join-search-console
   # uv run python ai-overview-rewrite-queue-api-example.py --example find-top4-never-cited
   ```

### Alternative: set the API key directly
```bash
export APIFY_API_TOKEN="your_api_key_here"
uv run python ai-overview-rewrite-queue-api-example.py
```

> **Cost note:** This is a composition Actor. A single run bills your Apify account for both this Actor's events and the child citation Actor's events (`johnvc/google-ai-overview-api`), so every query is billed twice, not once. The examples in this repo deliberately check only 2 to 3 queries so your first run stays inexpensive. Raise the input sizes once you know your budget.

## Why Use This AI Overview Rewrite Queue API?

Most AI visibility and ai search visibility tools give you a citation tracking feed: a list of who was cited. That tells you the score, not the move. This API joins the citation data to your own Search Console numbers so the output is already prioritized by lost opportunity.

The tiering is the point. Tier A is the money tier: you rank 5 to 20 and a competitor is cited in the AI Overview instead of you, so a rewrite has both room to climb and a citation to win. Tier B is the answer-shape blind spot: you rank in the top four and the AI still ignores you. Tier C flags pages that are cited but converting below your own baseline. Tier D means no rewrite action is indicated, and Tier X marks the rows it could not resolve, so an unknown is never disguised as a zero.

It is honest about uncertainty. When the citation check does not complete, the overview fields come back null, never a misleading false, and `check_status` says why. When Search Console anonymizes a low-volume query, the row is labeled `join_status: check_only` rather than dropped. That distinction matters for anyone doing serious GEO (generative engine optimization) or AEO (answer engine optimization) work, where a lost citation and a different exit region look identical unless you pin `gl`, `hl`, and `location` deliberately.

It runs from Python, from the Apify Console, on a schedule, or as an MCP tool inside Claude, Cursor, and ChatGPT. Point it at a published Google Sheet CSV of your export and a scheduled run picks up fresh data every time.

## Features

### Core Capabilities
- Joins a Google Search Console Queries export to live AI Overview citation data, one JSON row per query.
- Scores every query into a tier (A to X) with a plain-language `tier_reason`.
- Reports the full citation picture per query: `ai_overview_present`, `citation_state`, `reference_domains`, `reference_count`, `cited_urls`, `cited_pages_count`.
- Accepts the export as a published CSV URL or as pasted JSON rows, and lets you add extra `queries` to check.
- Handles localized headers, semicolon delimiters, and comma decimals in the export.
- Country, language, and named-location targeting (`gl`, `hl`, `location`) so citation checks are reproducible.

### Data Quality
- `join_status` labels each row as `matched`, `gsc_only`, or `check_only` so anonymized queries are never silently dropped.
- `check_status` (`ok`, `retrieval_failed`, `blocked`) tells you when the overview fields are trustworthy; on anything but `ok` they are null, never false.
- CTR is normalized to a fraction between 0 and 1 regardless of the export's original format.
- A run summary is written to the key-value store for auditing.

## Recipes

Each recipe below is a published, ready-to-run task on Apify. The top three also ship as local Python helpers in `ai-overview-rewrite-queue-api-example.py`.

### Find which pages to rewrite first for AI Overviews

[Run this on Apify](https://apify.com/johnvc/ai-overview-rewrite-queue/examples/find-which-pages-to-rewrite-first-for-ai-overviews?fpr=9n7kx3): send your domains and a Search Console export, and read the Tier A rows, the queries where you rank 5 to 20 and a competitor is cited instead of you.

Local: `uv run python ai-overview-rewrite-queue-api-example.py --example find-pages-to-rewrite-first`

### Join a Search Console export with AI Overview data

[Run this on Apify](https://apify.com/johnvc/ai-overview-rewrite-queue/examples/join-a-search-console-export-with-ai-overview-data?fpr=9n7kx3): send a Search Console Queries export and your domains, and get one JSON row per query with clicks, impressions, position, citation state, tier, and reason.

Local: `uv run python ai-overview-rewrite-queue-api-example.py --example join-search-console`

### Find pages that rank top 4 but are never cited by AI

[Run this on Apify](https://apify.com/johnvc/ai-overview-rewrite-queue/examples/find-pages-that-rank-top-4-but-are-never-cited-by-ai?fpr=9n7kx3): surfaces the Tier B queries where you rank in the top four and the AI Overview still ignores you, an answer-shape problem no ranking report will show.

Local: `uv run python ai-overview-rewrite-queue-api-example.py --example find-top4-never-cited`

### Track AI Overview citations monthly

[Run this on Apify](https://apify.com/johnvc/ai-overview-rewrite-queue/examples/track-ai-overview-citations-monthly?fpr=9n7kx3): connect a Search Console export each month, check which queries show an AI Overview and which domains it cited, and get the tiered queue back as structured JSON.

### Get the rewrite queue in Claude via MCP

[Run this on Apify](https://apify.com/johnvc/ai-overview-rewrite-queue/examples/get-rewrite-queue-in-claude-via-mcp?fpr=9n7kx3): call this API through the Apify MCP server so an AI assistant reads the tiered queue directly and finds the top-ranking pages the AI Overview never cites. See the install sections below.

**Schedule tip:** Publish your Search Console Queries export as a CSV (in Google Sheets: File, Share, Publish to web, comma-separated values), save that input as an Apify Task, and [schedule it](https://apify.com/johnvc/ai-overview-rewrite-queue?fpr=9n7kx3) to run monthly. Each run picks up fresh Search Console data automatically, so the rewrite queue stays current without manual runs.

## Google Search Console AI Overview

The wedge this API fills is the join itself: nothing in Search Console tells you whether Google's AI Overview cited you, and nothing in a citation feed tells you what that query is worth to you. This API is the missing link between the two. Feed it a Google Search Console AI Overview workflow, your Queries export plus your domains, and every row carries both halves at once: the Search Console `clicks`, `impressions`, `ctr`, and `position`, joined to the AI Overview `citation_state` and `reference_domains`. That is what makes the queue actionable instead of merely informative.

## Search Console AI Overview

A Search Console AI Overview check answers a question the Search Console UI cannot: for the queries where you already have impressions, is Google's AI answering with your content or someone else's? The `join_status` field keeps this honest. A `matched` row appears in both your export and the citation check. A `gsc_only` row was in the export but not checked. A `check_only` row was checked but is missing from the export, usually because Search Console anonymizes low-volume queries. Because the two data sources are labeled per row, you can trust the citation rate you compute from the output rather than guessing which side a number came from.

## Usage Examples

### Basic Example
```json
{
  "target_domains": ["example.com"],
  "search_console_rows": [
    { "query": "what is a crm", "clicks": 12, "impressions": 1900, "ctr": "0.63%", "position": 8.4 },
    { "query": "crm pricing guide", "clicks": 40, "impressions": 2600, "ctr": "1.54%", "position": 3.1 }
  ],
  "queries": ["best crm for small business"],
  "min_impressions": 5,
  "gl": "us",
  "hl": "en"
}
```

### Advanced Example
```json
{
  "target_domains": ["example.com", "learn.example.com"],
  "search_console_csv_url": "https://docs.google.com/spreadsheets/d/.../pub?output=csv",
  "queries": ["best crm for small business", "crm for real estate"],
  "min_impressions": 25,
  "gl": "gb",
  "hl": "en",
  "location": "London, England, United Kingdom"
}
```

## Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target_domains` | `array[str]` | YES | - | Domains you consider yours, for example `example.com`. Each result is classified by whether any of these was cited. Subdomains match their parent (`learn.example.com` matches `example.com`). |
| `search_console_csv_url` | `str` | no | `""` | URL of a Search Console Queries export (CSV) with the standard Query, Clicks, Impressions, CTR, Position columns. A published Google Sheet URL lets scheduled runs pick up fresh data. |
| `search_console_rows` | `array[object]` | no | - | An alternative to the URL: rows as JSON objects with `query`, `clicks`, `impressions`, `ctr`, `position`. Combined with the URL when both are given. |
| `queries` | `array[str]` | no | - | Keywords to check on top of the export. Leave empty to check exactly the queries in the export. |
| `min_impressions` | `int` | no | `10` | Ignore export rows below this impression count. Raising it focuses the queue on queries worth a rewrite. |
| `gl` | `str` | no | `us` | Two-letter country code for the citation checks (ISO 3166-1, for example `us`, `gb`, `ca`). |
| `hl` | `str` | no | `en` | Two-letter interface language code (ISO 639-1). AI Overviews are currently shown for English searches. |
| `location` | `str` | no | - | Optionally narrow the citation checks to a named location, for example `Austin, Texas, United States`. |

## Output Format

Each scored query is one row. Error conditions come back as an `error` row carrying `error_type` and `error_message` instead of scores.

```json
{
  "result_type": "scored_query",
  "query": "best crm for small business",
  "query_normalized": "best crm for small business",
  "tier": "A",
  "tier_reason": "You rank at position 8.0 and a competitor is cited in the AI Overview instead of you, on 1,900 impressions.",
  "join_status": "matched",
  "clicks": 42,
  "impressions": 1900,
  "ctr": 0.0221,
  "position": 8.4,
  "check_status": "ok",
  "ai_overview_present": true,
  "citation_state": "competitor_cited",
  "cited_urls": ["https://example.com/guides/crm"],
  "cited_pages_count": 1,
  "reference_domains": ["rival.com", "example.com"],
  "reference_count": 6,
  "fetched_at": "2026-08-17T14:02:11.482913+00:00"
}
```

| Field | Meaning |
|-------|---------|
| `result_type` | `scored_query` for a scored row, `error` for a row describing why the run could not proceed. |
| `query` / `query_normalized` | The query as written, and the lowercased, whitespace-collapsed form used for the join. |
| `tier` / `tier_reason` | The A to X tier and a one-sentence explanation. |
| `join_status` | `matched`, `gsc_only`, or `check_only`. |
| `clicks` / `impressions` / `ctr` / `position` | Search Console fields, null when the query was not in the export. |
| `check_status` | `ok`, `retrieval_failed`, or `blocked`. On anything but `ok` the overview fields are null. |
| `ai_overview_present` | Whether an AI Overview appeared. False means checked and none appeared; null means it could not be checked. |
| `citation_state` | `no_overview`, `cited`, `competitor_cited`, or `overview_no_references`. |
| `cited_urls` / `cited_pages_count` | Your reference links that the AI Overview cited, and how many. |
| `reference_domains` / `reference_count` | Every domain the AI Overview cited, in order, and how many sources it cited. |
| `fetched_at` | UTC timestamp for when the row was produced. |
| `error_message` / `error_type` | Present only on an `error` row. |

## People also search for

### How do I track AI Overviews?

Run this API with your domains and a Search Console Queries export, published as a CSV so a scheduled run refreshes it. Each run checks whether an AI Overview appeared for every query and which domains it cited, then scores the query into a tier. Save the input as an Apify Task and schedule it monthly for ongoing ai overview tracking. See the Recipes and the install sections below.

### How do I improve brand visibility in AI search engines?

Start with the Tier A queue. Those are queries where you already rank 5 to 20 and a competitor is cited in the AI Overview instead of you, so a rewrite has both headroom in the ranking and a citation to capture. The `reference_domains` field shows who is being cited, and `tier_reason` explains why each page landed where it did, so you rewrite the pages with the most to gain first rather than guessing.

### What strategies improve brand visibility in AI search engines?

The output points at two distinct strategies. Tier A is a competitive-displacement play: you rank near the citation but a rival holds it, so match the answer shape the overview rewards. Tier B is a coverage gap: you rank in the top four yet the AI ignores you entirely, which usually means the page answers the query for a human reader but not in the extractable form an answer engine pulls from. Because the queue separates the two, you apply the right fix to each page instead of one blanket rewrite.

### What is answer engine optimization (AEO) vs SEO?

Classic SEO optimizes for rank, where your page sits in the ten blue links. Answer engine optimization (AEO), closely related to GEO (generative engine optimization), optimizes for citation, whether an AI Overview quotes and links you at all. They are different problems, and a page can win one while losing the other. This API measures both at once: `position` is the SEO signal, `citation_state` is the AEO signal, and the tiering is built precisely on the gap between them.

### Why are some rows in the queue with no clicks or impressions?

Those are `join_status: check_only` rows. The query was checked for an AI Overview but is missing from your Search Console export, usually because Search Console anonymizes low-volume queries. They are kept, not dropped, so you can see coverage the export hides. Rows the export has but the check skipped are labeled `gsc_only`.

### Can I use this AI Overview Rewrite Queue API with MCP or Claude?

Yes. Use the install sections below to add the Actor as an MCP tool in [Claude Code](https://claude.ai/referral/uIlpa7nPLg) (free trial), [Claude Cowork](https://claude.ai/referral/uIlpa7nPLg) (free trial), Claude.ai, Cursor, or ChatGPT, then ask the assistant to build and read your rewrite queue.

---

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the AI Overview Rewrite Queue API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/ai-overview-rewrite-queue"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the AI Overview Rewrite Queue API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

---

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/ai-overview-rewrite-queue"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/ai-overview-rewrite-queue" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the AI Overview Rewrite Queue API.

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

---

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/ai-overview-rewrite-queue`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/ai-overview-rewrite-queue`, using OAuth when prompted.
5. Ask Claude to run the AI Overview Rewrite Queue API.

Open Claude on the web: https://claude.ai

---

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/ai-overview-rewrite-queue"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/ai-overview-rewrite-queue",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the AI Overview Rewrite Queue API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

---

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/ai-overview-rewrite-queue`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

## 🌐 About Alpha OSINT

This example repo is part of [Alpha OSINT](https://www.alphaosint.com), toolset of financial and operations data sources and APIs.
See the [AI Overview Rewrite Queue source page](https://www.alphaosint.com/sources/ai-overview-rewrite-queue/) for related tools and use cases.
For support or requests for this actor, please start a ticket [directly on our support page](https://apify.com/johnvc/ai-overview-rewrite-queue/issues/open?fpr=9n7kx3).

---

[**Made with care**](https://apify.com/johnvc?fpr=9n7kx3)

*Use the AI Overview Rewrite Queue API to power your ai overview tracking with reliable, structured results.*

Last Updated: 2026.09.12
