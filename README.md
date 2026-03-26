### deconstructed-papers-skill

```markdown
# Deconstructed Papers — Python CLI & API Skill

Python CLI and machine-readable API documentation for [Deconstructed Papers](https://www.deconstructedpapers.com) — parse academic PDFs into structured data and create shareable links.

## Quick Start

```bash
curl -O https://raw.githubusercontent.com/nighthawk6389/deconstructed-papers-skill/main/auto-share.py
pip install requests
export DP_API_KEY="dp_live_..."

# Parse a paper
python auto-share.py parse https://arxiv.org/abs/1706.03762

# Parse and create a shared link
python auto-share.py share https://arxiv.org/abs/1706.03762
```

## Setup

1. **Create an account** at [deconstructedpapers.com](https://www.deconstructedpapers.com)
2. **Create an API key** at **Settings → API Keys** — the key is shown once, save it immediately
3. **Set the key** as an environment variable:

```bash
export DP_API_KEY="dp_live_..."
```

## CLI Reference

The CLI is a single-file Python script (`auto-share.py`) with no dependencies beyond `requests`.

### Parse Papers

Returns structured paper data (title, authors, sections with LaTeX). Costs 1 credit per fresh parse; cached results are free.

```bash
# Parse a single paper
python auto-share.py parse https://arxiv.org/abs/1706.03762

# Parse with a specific model
python auto-share.py parse --model anthropic/claude-sonnet-4.6 URL

# Raw JSON output (for piping to jq, etc.)
python auto-share.py parse --json URL

# Quiet mode — titles only
python auto-share.py parse -q URL1 URL2
```

### Create Shared Links

Parses the paper and generates a shareable URL in one step.

```bash
# Share a single paper
python auto-share.py share https://arxiv.org/abs/1706.03762

# Batch share
python auto-share.py share URL1 URL2 URL3

# Quiet mode — URLs only (useful for scripting)
python auto-share.py share -q URL1 URL2
```

### Manage API Keys

```bash
python auto-share.py keys list
python auto-share.py keys create --name "my-bot"
python auto-share.py keys revoke KEY_UUID
```

### Global Options

| Flag | Env Var | Description |
|------|---------|-------------|
| `--api-key` | `DP_API_KEY` | API key for all commands |
| `--base-url` | `DP_BASE_URL` | Override base URL (default: `https://www.deconstructedpapers.com`) |

### Local Development

```bash
python auto-share.py --base-url http://localhost:3000 parse URL
```

## Key Behaviors

- **Caching**: Same URL + same user = cache hit. No credit deducted.
- **arXiv normalization**: `/abs/` URLs auto-convert to `/pdf/`.
- **Retries**: The CLI retries up to 3 times on network errors, 5xx, and 429s with exponential backoff.
- **Default model**: `anthropic/claude-haiku-4.5` (fast, cost-effective).

## API Documentation

- **Human-readable docs**: [deconstructedpapers.com/docs](https://www.deconstructedpapers.com/docs)
- **Machine-readable (for LLMs/agents)**: [`llms.txt`](./llms.txt) or [deconstructedpapers.com/llms.txt](https://www.deconstructedpapers.com/llms.txt)

## For AI Agents (Claude Code Skill)

The [`SKILL.md`](./SKILL.md) file can be used as a Claude Code skill. It provides structured instructions for using the Deconstructed Papers API via the Python CLI.
```

---

### SKILL.md

```markdown
---
name: dp-api
description: Use the Deconstructed Papers API via the Python CLI to parse papers and create shared links
---

# Deconstructed Papers API — Python CLI

Use this skill when the user wants to parse papers, create shared links, or manage API keys via the Deconstructed Papers API.

For full API endpoint documentation (request/response schemas, error codes, rate limits, curl examples), see https://www.deconstructedpapers.com/docs

## Setup

```bash
curl -O https://raw.githubusercontent.com/nighthawk6389/deconstructed-papers-skill/main/auto-share.py
pip install requests
export DP_API_KEY="dp_live_..."
```

API keys are created in the web app at **Settings → API Keys**. The key is shown once — save it immediately.

## CLI Reference

The CLI is a single-file script: [`auto-share.py`](https://github.com/nighthawk6389/deconstructed-papers-skill/blob/main/auto-share.py)

### Parse Papers

Returns structured paper data (title, authors, sections with LaTeX). Costs 1 credit per fresh parse; cached results are free.

```bash
# Parse a single paper
python auto-share.py parse https://arxiv.org/abs/1706.03762

# Parse with a specific model
python auto-share.py parse --model anthropic/claude-sonnet-4.6 URL

# Raw JSON output (for piping to jq, etc.)
python auto-share.py parse --json URL

# Quiet mode — titles only
python auto-share.py parse -q URL1 URL2
```

### Create Shared Links

Parses the paper and generates a shareable URL in one step.

```bash
# Share a single paper
python auto-share.py share https://arxiv.org/abs/1706.03762

# Batch share
python auto-share.py share URL1 URL2 URL3

# Quiet mode — URLs only (useful for scripting)
python auto-share.py share -q URL1 URL2
```

### Manage API Keys

```bash
python auto-share.py keys list
python auto-share.py keys create --name "my-bot"
python auto-share.py keys revoke KEY_UUID
```

### Global Options

| Flag | Env Var | Description |
|------|---------|-------------|
| `--api-key` | `DP_API_KEY` | API key for all commands |
| `--base-url` | `DP_BASE_URL` | Override base URL (default: `https://www.deconstructedpapers.com`) |

### Local Development

```bash
python auto-share.py --base-url http://localhost:3000 parse URL
```

## Key Behaviors

- **Caching**: Same URL + same user = cache hit. No credit deducted.
- **arXiv normalization**: `/abs/` URLs auto-convert to `/pdf/`.
- **Retries**: The CLI retries up to 3 times on network errors, 5xx, and 429s with exponential backoff.
- **Default model**: `anthropic/claude-haiku-4.5` (fast, cost-effective).
```

---

### llms.txt

```
# Deconstructed Papers API

> Deconstructed Papers is a tool that uses LLMs to parse academic PDFs into structured sections and provides AI explanations, math analysis, and artifact generation.

## Documentation

Human-readable docs: https://www.deconstructedpapers.com/docs

## Base URL

Production: https://www.deconstructedpapers.com

## Authentication

All API endpoints require an API key as a Bearer token.

Create keys in the web app at Settings → API Keys, or programmatically via the /api/keys endpoint.

```
Authorization: Bearer dp_live_your_key_here
```

### Managing API Keys

All key management endpoints accept Bearer token auth.

```
GET /api/keys
Headers:
  Authorization: Bearer dp_live_...
Response: { "keys": [{ "id": "uuid", "name": "my-bot", "keyPrefix": "dp_live_abc12345...", "lastUsedAt": "...", "createdAt": "..." }] }
```

```
POST /api/keys
Headers:
  Authorization: Bearer dp_live_...
  Content-Type: application/json
Body: { "name": "my-bot" }
Response: { "key": "dp_live_...", "id": "uuid", "name": "my-bot", "keyPrefix": "dp_live_abc12345...", "createdAt": "..." }
```

The `key` field is the full API key, shown exactly once. Store it securely — it cannot be retrieved again.

```
DELETE /api/keys
Headers:
  Authorization: Bearer dp_live_...
  Content-Type: application/json
Body: { "keyId": "uuid" }
Response: { "success": true }
```

### Limits

- Maximum 5 active API keys per user

## Auto-Parse Endpoint

Parse a PDF from a URL and get the structured paper data. Does not create a share link.

```
POST /api/papers/auto-parse
Headers:
  Content-Type: application/json
  Authorization: Bearer dp_live_...
Body:
  {
    "url": "https://arxiv.org/abs/2301.12345",
    "model": "anthropic/claude-haiku-4.5"  // optional
  }
```

### Response (success)

```json
{
  "title": "Attention Is All You Need",
  "authors": ["Ashish Vaswani", "Noam Shazeer", "..."],
  "paper": {
    "title": "Attention Is All You Need",
    "authors": ["Ashish Vaswani", "..."],
    "abstract": "...",
    "sections": [
      {
        "id": "1",
        "heading": "Introduction",
        "type": "text",
        "content": [{ "type": "text", "value": "..." }],
        "pageNumbers": [1, 2]
      }
    ]
  },
  "cached": false
}
```

The `paper` field contains the full structured paper with sections, content blocks, and math expressions.

## Auto-Share Endpoint

Parse a PDF from a URL and get a shareable link in one step.

```
POST /api/papers/auto-share
Headers:
  Content-Type: application/json
  Authorization: Bearer dp_live_...
Body:
  {
    "url": "https://arxiv.org/abs/2301.12345",
    "model": "anthropic/claude-haiku-4.5"  // optional
  }
```

### Response (success)

```json
{
  "shortCode": "abc12345",
  "url": "/s/abc12345",
  "title": "Attention Is All You Need",
  "authors": ["Ashish Vaswani", "Noam Shazeer", "..."],
  "cached": false
}
```

The full shareable URL is `https://www.deconstructedpapers.com/s/{shortCode}`.

## Shared Behavior (both endpoints)

### Caching

If the same URL has been parsed before by the same user, the endpoint returns the cached result with `"cached": true` and does not deduct a credit.

### Credits

- A fresh parse (cache miss) costs 1 credit
- A cache hit costs 0 credits
- If parsing fails for any reason, the credit is automatically refunded
- If you have no credits, the endpoint returns HTTP 402

### Available Models

| Model ID | Name |
|----------|------|
| `anthropic/claude-haiku-4.5` | Claude Haiku 4.5 (default) |
| `anthropic/claude-sonnet-4.6` | Claude Sonnet 4.6 |
| `google/gemini-2.5-pro` | Gemini 2.5 Pro |
| `google/gemini-2.5-flash` | Gemini 2.5 Flash |

### Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Invalid request (bad URL, HTML instead of PDF, invalid magic bytes) |
| 401 | Missing or invalid authentication |
| 402 | No credits remaining |
| 403 | Publisher blocks automated PDF downloads |
| 413 | PDF too large for selected model |
| 429 | Rate limit exceeded (check `Retry-After` header) |
| 502 | PDF fetch or LLM parsing failed |
| 500 | Internal server error |

### Rate Limits

Both endpoints share rate limits with the parse-paper endpoint:

| Tier | Limit |
|------|-------|
| Free | 10 per day |
| Pro | 20 per hour |

### URL Handling

- arXiv URLs are automatically normalized (e.g., `/abs/` → `/pdf/`, routed through `export.arxiv.org`)
- Any valid HTTPS PDF URL is accepted
- Private/internal IP addresses and non-HTTP(S) protocols are blocked

## Shared Paper Viewing

Shared papers are publicly viewable at `/s/{shortCode}` — no authentication required.

## Python CLI

A Python CLI tool is available at: https://github.com/nighthawk6389/deconstructed-papers-skill

Download: https://raw.githubusercontent.com/nighthawk6389/deconstructed-papers-skill/main/auto-share.py

```bash
curl -O https://raw.githubusercontent.com/nighthawk6389/deconstructed-papers-skill/main/auto-share.py
pip install requests
export DP_API_KEY="dp_live_..."

# Parse a paper
python auto-share.py parse https://arxiv.org/abs/1706.03762

# Parse and create a shared link
python auto-share.py share https://arxiv.org/abs/1706.03762

# Manage API keys
python auto-share.py keys list
python auto-share.py keys create --name my-bot
python auto-share.py keys revoke KEY_ID
```
```
