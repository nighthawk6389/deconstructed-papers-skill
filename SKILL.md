---
name: dp-api
description: Use the Deconstructed Papers API via the Python CLI to parse papers and create shared links
---

# Deconstructed Papers API — Python CLI

Use this skill when the user wants to parse papers, create shared links, or manage API keys via the Deconstructed Papers API.

For full API endpoint documentation (request/response schemas, error codes, rate limits, curl examples), see `docs/api-usage.md`.

## Setup

```bash
pip install requests
export DP_API_KEY="dp_live_..."
```

API keys are created in the web app at **Settings → API Keys**. The key is shown once — save it immediately.

## CLI Reference

The CLI lives at `scripts/auto-share.py`.

### Parse Papers

Returns structured paper data (title, authors, sections with LaTeX). Costs 1 credit per fresh parse; cached results are free.

```bash
# Parse a single paper
python scripts/auto-share.py parse https://arxiv.org/abs/1706.03762

# Parse with a specific model
python scripts/auto-share.py parse --model anthropic/claude-sonnet-4.6 URL

# Raw JSON output (for piping to jq, etc.)
python scripts/auto-share.py parse --json URL

# Quiet mode — titles only
python scripts/auto-share.py parse -q URL1 URL2
```

### Create Shared Links

Parses the paper and generates a shareable URL in one step.

```bash
# Share a single paper
python scripts/auto-share.py share https://arxiv.org/abs/1706.03762

# Batch share
python scripts/auto-share.py share URL1 URL2 URL3

# Quiet mode — URLs only (useful for scripting)
python scripts/auto-share.py share -q URL1 URL2
```

### Manage API Keys

```bash
python scripts/auto-share.py keys list
python scripts/auto-share.py keys create --name "my-bot"
python scripts/auto-share.py keys revoke KEY_UUID
```

### Global Options

| Flag | Env Var | Description |
|------|---------|-------------|
| `--api-key` | `DP_API_KEY` | API key for all commands |
| `--base-url` | `DP_BASE_URL` | Override base URL (default: `https://www.deconstructedpapers.com`) |

### Local Development

```bash
python scripts/auto-share.py --base-url http://localhost:3000 parse URL
```

## Key Behaviors

- **Caching**: Same URL + same user = cache hit. No credit deducted.
- **arXiv normalization**: `/abs/` URLs auto-convert to `/pdf/`.
- **Retries**: The CLI retries up to 3 times on network errors, 5xx, and 429s with exponential backoff.
- **Default model**: `anthropic/claude-haiku-4.5` (fast, cost-effective).
