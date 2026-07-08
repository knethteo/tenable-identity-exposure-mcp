# Tenable Identity Exposure MCP Server

An [MCP](https://modelcontextprotocol.io) server exposing the **Tenable Identity Exposure** (TIE, formerly Tenable.ad) REST API as tools for LLM clients. Built on `FastMCP` from the official `mcp` SDK.

Verified end-to-end against a live TIE SaaS instance (`v3.120.1`).

> ⚠️ **Disclaimer:** This is **not an officially supported Tenable project**. It was
> built with assistance from Claude — treat its output as a starting point and
> validate responses against the Tenable console before acting on them.

## Tools

| Tool | Description |
|---|---|
| `tie_catalog` | List available resources (flat + nested) — call this first |
| `tie_request` | Raw HTTP call to any endpoint (`method`, `path`, `params`, `body`) |
| `tie_resource_action` | Generic CRUD (`list`/`get`/`create`/`update`/`delete`) on flat resources |
| `tie_recent_activity` | **Unified IoE+IoA timeline for the last N hours (one call)** |
| `tie_profiles` | List security profiles (IoE/IoA data is profile-scoped) |
| `tie_scores` | Per-directory security scores for a profile |
| `tie_topology` | AD topology (domains, forests, trusts) for a profile |
| `tie_attacks` | IoA attack instances (requires `resource_type` + `resource_value`) |
| `tie_alerts` | Alerts for a profile |
| `tie_deviances` | IoE deviant AD objects for a checker within a **time window** |
| `tie_deviances_by_checker` | Full IoE deviances for a checker (no date filter) |
| `tie_deviances_by_directory` | Full IoE deviances for a directory (no date filter) |
| `tie_search_events` | Search AD security events in a date range |
| `tie_search_ad_objects` | Search AD objects (users/computers/groups/OUs) |
| `tie_whoami` | Current user identity, roles, permissions |

### Time windows, profiles, and token budget

- Time-aware tools (`tie_recent_activity`, `tie_deviances`) accept a relative
  `hours=N` window or explicit `date_start`/`date_end`. All timestamps are **UTC**.
- IoE/IoA data is **profile-scoped**. The API does not expose which profile your
  console has selected, so pass `profile_id` explicitly — use `tie_profiles` to list them.
- By default, deviance/object results are **slimmed**: descriptions are rendered
  from their templates and oversized attribute values (SID lists, member dumps)
  are dropped. Pass `verbose=true` for the full raw payload.

## Configuration

Set via environment variables (or `--tie-url` / `--tie-api-key` flags):

| Variable | Description |
|---|---|
| `TIE_URL` | Base URL, e.g. `https://your-host.tenable.ad` |
| `TIE_API_KEY` | API key (TIE console → **System → Configuration → API key**) |
| `TIE_VERIFY_SSL` | `true` (default) or `false` for self-signed certs |

Auth uses the `X-API-Key` header.

## Install & run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .

cp .env.example .env   # fill in TIE_URL and TIE_API_KEY

# stdio (Claude Desktop / Claude Code)
set -a; . ./.env; set +a
tenable-tie-mcp

# or network transports
tenable-tie-mcp --transport sse --port 8000
tenable-tie-mcp --transport http --port 8000
```

### Running with uv / uvx (alternative to a manual venv)

[uv](https://docs.astral.sh/uv/) can manage the environment for you. `uv` is the
full tool; `uvx` (alias for `uv tool run`) runs a package in a throwaway env, like
`npx`. Both need `uv` installed (`brew install uv`).

```bash
# uv run: resolves deps from pyproject.toml into a managed .venv, then runs
uv run tenable-tie-mcp

# uvx: run ephemerally from the project path, nothing persisted
uvx --from . tenable-tie-mcp
```

## Claude Desktop / Claude Code config

Use the **full path** to the executable. Claude Desktop does not launch from your
shell, so it does not inherit your `PATH` — a bare `tenable-tie-mcp` will fail with
"command not found" unless the tool is on the system PATH (e.g. a `pipx` install).

For a venv install, point at the venv's launcher:

```json
{
  "mcpServers": {
    "tenable-tie": {
      "command": "/absolute/path/to/tenable-ie-mcp/.venv/bin/tenable-tie-mcp",
      "env": {
        "TIE_URL": "https://your-host.tenable.ad",
        "TIE_API_KEY": "your-key"
      }
    }
  }
}
```

Find the exact path with `echo "$PWD/.venv/bin/tenable-tie-mcp"` from the project
root. See `claude_desktop_config.sample.json` for a complete example.

> If you installed globally with `pipx install .` (or `uv tool install`), the bare
> `"command": "tenable-tie-mcp"` works because it lands on the system PATH.

### With uv (alternative)

Point `command` at the **full path** of `uv` (`which uv`, e.g. `/opt/homebrew/bin/uv`)
and let it manage the environment:

```json
{
  "mcpServers": {
    "tenable-tie": {
      "command": "/opt/homebrew/bin/uv",
      "args": ["run", "--directory", "/absolute/path/to/tenable-ie-mcp", "tenable-tie-mcp"],
      "env": {
        "TIE_URL": "https://your-host.tenable.ad",
        "TIE_API_KEY": "your-key"
      }
    }
  }
}
```

## Docker

```bash
docker compose up --build   # reads TIE_URL / TIE_API_KEY from environment
```

## Example prompts

- "Show me IoE and IoA activity in the last 12 hours." → `tie_recent_activity`
- "Which security profiles exist?" → `tie_profiles`
- "List the monitored directories and their security scores."
- "Show the latest IoA attacks against directory 8."
- "What IoE deviances appeared for checker 15 in the last day?" → `tie_deviances`
- "Show unread alerts for profile 2."

## Notes

- `profile_id` defaults to `1` (the default Tenable profile) in the convenience tools.
- Attacks must be scoped: `resource_type` ∈ `infrastructure|directory|hostname|ip`
  and `resource_value` is the id or name/ip.
- Non-JSON responses are returned as `{"content_type": ..., "text": ...}` rather
  than crashing.
- **Scoring and prioritization:** TIE checkers carry a `remediationCost` (easy / medium /
  hard) but no native asset-level severity score. If your workflow requires
  **AES (Asset Exposure Score)** or **ACR (Asset Criticality Rating)** — for example,
  to rank affected identities by business risk — connect your environment to
  [Tenable One](https://www.tenable.com/products/tenable-one). Tenable One aggregates
  data across TIE, Tenable Vulnerability Management, and other sources to produce
  unified AES/ACR scores that can be surfaced here via the API.
