---
name: deconstructed-papers
description: Parse papers and generate Deconstructed Papers share links using the bundled Python CLI and Deconstructed Papers API. Use when the user wants to turn arXiv/PDF URLs into structured paper output or public share links, especially for batch paper workflows, arXiv discovery pipelines, or automated publishing flows.
---

# Deconstructed Papers API

Use this skill to parse papers and create share links via Deconstructed Papers.

## What it does

- Parse a paper URL into structured sections
- Create a shareable Deconstructed Papers link
- Batch process multiple paper URLs
- Manage API keys when explicitly asked

## Authentication

The API key is expected in one of these ways:

- `DP_API_KEY` environment variable
- `--api-key` CLI flag

In this workspace, the key may already exist in:

- `/home/javaiye/.openclaw/workspace/.env`

If needed before running the script:

```bash
source /home/javaiye/.openclaw/workspace/.env
```

## Script

Use the bundled script:

```bash
python3 /home/javaiye/.openclaw/workspace/skills/deconstructed-papers/scripts/auto-share.py ...
```

## Common usage

### Parse one paper

```bash
source /home/javaiye/.openclaw/workspace/.env
python3 /home/javaiye/.openclaw/workspace/skills/deconstructed-papers/scripts/auto-share.py parse https://arxiv.org/abs/1706.03762
```

### Parse with JSON output

```bash
source /home/javaiye/.openclaw/workspace/.env
python3 /home/javaiye/.openclaw/workspace/skills/deconstructed-papers/scripts/auto-share.py parse --json https://arxiv.org/abs/1706.03762
```

### Share one paper

```bash
source /home/javaiye/.openclaw/workspace/.env
python3 /home/javaiye/.openclaw/workspace/skills/deconstructed-papers/scripts/auto-share.py share https://arxiv.org/abs/1706.03762
```

### Batch share

```bash
source /home/javaiye/.openclaw/workspace/.env
python3 /home/javaiye/.openclaw/workspace/skills/deconstructed-papers/scripts/auto-share.py share URL1 URL2 URL3
```

### Quiet mode for pipelines

```bash
source /home/javaiye/.openclaw/workspace/.env
python3 /home/javaiye/.openclaw/workspace/skills/deconstructed-papers/scripts/auto-share.py share -q URL1 URL2
```

## Notes

- arXiv `/abs/` URLs are normalized to `/pdf/` by the CLI.
- Cached papers do not consume fresh parse credits.
- The script retries transient failures and rate limits.
- Default model is `anthropic/claude-haiku-4.5` unless overridden.

## Key management

Only use key-management commands when the user explicitly asks:

```bash
python3 /home/javaiye/.openclaw/workspace/skills/deconstructed-papers/scripts/auto-share.py keys list
python3 /home/javaiye/.openclaw/workspace/skills/deconstructed-papers/scripts/auto-share.py keys create --name "my-bot"
python3 /home/javaiye/.openclaw/workspace/skills/deconstructed-papers/scripts/auto-share.py keys revoke KEY_UUID
```

## Reference docs

For full API documentation:

- https://www.deconstructedpapers.com/docs
