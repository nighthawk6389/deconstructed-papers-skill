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

