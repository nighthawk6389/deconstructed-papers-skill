#!/usr/bin/env python3
"""
Deconstructed Papers CLI — parse papers, create shared links, manage API keys.

Usage:
    export DP_API_KEY="dp_live_..."
    python auto-share.py parse https://arxiv.org/abs/1706.03762
    python auto-share.py parse --model anthropic/claude-sonnet-4.6 URL1 URL2
    python auto-share.py parse --json URL                    # raw JSON output
    python auto-share.py share https://arxiv.org/abs/1706.03762
    python auto-share.py share --model anthropic/claude-sonnet-4.6 URL1 URL2
    python auto-share.py keys create --name my-bot
    python auto-share.py keys list
    python auto-share.py keys revoke KEY_ID

Requirements:
    pip install requests
"""

import argparse
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    print(
        "Error: 'requests' package required. Install with: pip install requests",
        file=sys.stderr,
    )
    sys.exit(1)

DEFAULT_BASE_URL = "https://www.deconstructedpapers.com"
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # seconds


# ---------------------------------------------------------------------------
# HTTP helper with retries
# ---------------------------------------------------------------------------


def _post_with_retries(
    endpoint_url: str, api_key: str, payload: dict
) -> dict:
    """POST to an API endpoint with retry logic for network/server errors."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    last_error: str | None = None

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                endpoint_url,
                headers=headers,
                json=payload,
                timeout=300,
            )
        except requests.RequestException as e:
            last_error = str(e)
            if attempt < MAX_RETRIES - 1:
                wait = INITIAL_BACKOFF * (2**attempt)
                print(f"  Network error, retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            break

        if resp.status_code == 429:
            retry_after = int(
                resp.headers.get("Retry-After", INITIAL_BACKOFF * (2**attempt))
            )
            if attempt < MAX_RETRIES - 1:
                print(
                    f"  Rate limited, retrying in {retry_after}s...", file=sys.stderr
                )
                time.sleep(retry_after)
                continue
            last_error = "Rate limit exceeded"
            break

        if resp.status_code >= 500 and attempt < MAX_RETRIES - 1:
            wait = INITIAL_BACKOFF * (2**attempt)
            print(
                f"  Server error ({resp.status_code}), retrying in {wait}s...",
                file=sys.stderr,
            )
            time.sleep(wait)
            continue

        if not resp.ok:
            try:
                error = resp.json().get("error", resp.text)
            except ValueError:
                error = resp.text
            return {"error": error, "status": resp.status_code}

        return resp.json()

    return {"error": last_error or "Failed after retries", "status": 0}


# ---------------------------------------------------------------------------
# Shared link helpers
# ---------------------------------------------------------------------------


def auto_share(
    base_url: str, api_key: str, url: str, model: str | None = None
) -> dict:
    """Post a PDF URL to the auto-share endpoint and return the result."""
    payload: dict = {"url": url}
    if model:
        payload["model"] = model
    return _post_with_retries(f"{base_url}/api/papers/auto-share", api_key, payload)


# ---------------------------------------------------------------------------
# Parse helpers
# ---------------------------------------------------------------------------


def auto_parse(
    base_url: str, api_key: str, url: str, model: str | None = None
) -> dict:
    """Post a PDF URL to the auto-parse endpoint and return the parsed paper."""
    payload: dict = {"url": url}
    if model:
        payload["model"] = model
    return _post_with_retries(f"{base_url}/api/papers/auto-parse", api_key, payload)


# ---------------------------------------------------------------------------
# Key management helpers
# ---------------------------------------------------------------------------


def _bearer_headers(api_key: str) -> dict:
    """Headers for API key-authenticated requests."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }


def create_key(base_url: str, api_key: str, name: str) -> dict:
    """Create a new API key. Returns the full key (shown once)."""
    resp = requests.post(
        f"{base_url}/api/keys",
        headers=_bearer_headers(api_key),
        json={"name": name},
        timeout=30,
    )
    if not resp.ok:
        try:
            return {"error": resp.json().get("error", resp.text), "status": resp.status_code}
        except ValueError:
            return {"error": resp.text, "status": resp.status_code}
    return resp.json()


def list_keys(base_url: str, api_key: str) -> dict:
    """List all active API keys."""
    resp = requests.get(
        f"{base_url}/api/keys",
        headers=_bearer_headers(api_key),
        timeout=30,
    )
    if not resp.ok:
        try:
            return {"error": resp.json().get("error", resp.text), "status": resp.status_code}
        except ValueError:
            return {"error": resp.text, "status": resp.status_code}
    return resp.json()


def revoke_key(base_url: str, api_key: str, key_id: str) -> dict:
    """Revoke an API key by ID."""
    resp = requests.delete(
        f"{base_url}/api/keys",
        headers=_bearer_headers(api_key),
        json={"keyId": key_id},
        timeout=30,
    )
    if not resp.ok:
        try:
            return {"error": resp.json().get("error", resp.text), "status": resp.status_code}
        except ValueError:
            return {"error": resp.text, "status": resp.status_code}
    return resp.json()


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def cmd_parse(args: argparse.Namespace) -> None:
    """Handle the 'parse' subcommand."""
    if not args.api_key:
        print(
            "Error: API key required. Set DP_API_KEY or pass --api-key.",
            file=sys.stderr,
        )
        sys.exit(1)

    errors = 0
    for url in args.urls:
        if not args.quiet and not args.json_output:
            print(f"Processing: {url}")
        result = auto_parse(args.base_url, args.api_key, url, args.model)

        if "error" in result:
            print(
                f"  Error ({result.get('status', '?')}): {result['error']}",
                file=sys.stderr,
            )
            errors += 1
            continue

        if args.json_output:
            print(json.dumps(result, indent=2))
        elif args.quiet:
            print(result.get("title", "Unknown"))
        else:
            cached = " (cached)" if result.get("cached") else ""
            authors = result.get("authors", [])
            sections = result.get("paper", {}).get("sections", [])
            print(f"  Title:    {result.get('title', 'Unknown')}{cached}")
            if authors:
                print(f"  Authors:  {', '.join(authors)}")
            print(f"  Sections: {len(sections)}")
            print()

    if errors:
        sys.exit(1)


def cmd_share(args: argparse.Namespace) -> None:
    """Handle the 'share' subcommand."""
    if not args.api_key:
        print(
            "Error: API key required. Set DP_API_KEY or pass --api-key.",
            file=sys.stderr,
        )
        sys.exit(1)

    errors = 0
    for url in args.urls:
        if not args.quiet:
            print(f"Processing: {url}")
        result = auto_share(args.base_url, args.api_key, url, args.model)

        if "error" in result:
            print(
                f"  Error ({result.get('status', '?')}): {result['error']}",
                file=sys.stderr,
            )
            errors += 1
            continue

        full_url = f"{args.base_url}{result['url']}"
        if args.quiet:
            print(full_url)
        else:
            cached = " (cached)" if result.get("cached") else ""
            authors = result.get("authors", [])
            print(f"  Title:   {result.get('title', 'Unknown')}")
            if authors:
                print(f"  Authors: {', '.join(authors)}")
            print(f"  Link:    {full_url}{cached}")
            print()

    if errors:
        sys.exit(1)


def cmd_keys(args: argparse.Namespace) -> None:
    """Handle the 'keys' subcommand."""
    api_key = args.api_key
    if not api_key:
        print(
            "Error: API key required. Set DP_API_KEY or pass --api-key.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.keys_action == "create":
        result = create_key(args.base_url, api_key, args.name)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"API key created successfully!")
        print(f"  Name:   {result['name']}")
        print(f"  Key:    {result['key']}")
        print(f"  ID:     {result['id']}")
        print()
        print("  Save this key now — it will not be shown again.")

    elif args.keys_action == "list":
        result = list_keys(args.base_url, api_key)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        keys = result.get("keys", [])
        if not keys:
            print("No active API keys.")
            return
        print(f"{'Name':<20} {'Prefix':<25} {'Last Used':<22} {'ID'}")
        print("-" * 90)
        for k in keys:
            last_used = k.get("lastUsedAt") or "Never"
            print(f"{k['name']:<20} {k['keyPrefix']:<25} {last_used:<22} {k['id']}")

    elif args.keys_action == "revoke":
        result = revoke_key(args.base_url, api_key, args.key_id)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"API key {args.key_id} revoked successfully.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deconstructed Papers CLI — parse papers, create shared links, manage API keys.",
        epilog="See https://deconstructedpapers.com/llms.txt for full API docs.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("DP_BASE_URL", DEFAULT_BASE_URL),
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- parse subcommand ---
    parse_parser = subparsers.add_parser(
        "parse", help="Parse PDF URLs and return structured paper data"
    )
    parse_parser.add_argument("urls", nargs="+", help="PDF URLs to parse")
    parse_parser.add_argument(
        "--model", default=None, help="LLM model (default: claude-haiku-4.5)"
    )
    parse_parser.add_argument(
        "--api-key",
        default=os.environ.get("DP_API_KEY"),
        help="API key (default: $DP_API_KEY)",
    )
    parse_parser.add_argument(
        "--quiet", "-q", action="store_true", help="Only print paper titles"
    )
    parse_parser.add_argument(
        "--json", dest="json_output", action="store_true", help="Output raw JSON"
    )

    # --- share subcommand ---
    share_parser = subparsers.add_parser(
        "share", help="Parse PDF URLs and create shared links"
    )
    share_parser.add_argument("urls", nargs="+", help="PDF URLs to parse and share")
    share_parser.add_argument(
        "--model", default=None, help="LLM model (default: claude-haiku-4.5)"
    )
    share_parser.add_argument(
        "--api-key",
        default=os.environ.get("DP_API_KEY"),
        help="API key (default: $DP_API_KEY)",
    )
    share_parser.add_argument(
        "--quiet", "-q", action="store_true", help="Only print shared URLs"
    )

    # --- keys subcommand ---
    keys_parser = subparsers.add_parser("keys", help="Manage API keys")
    keys_parser.add_argument(
        "--api-key",
        default=os.environ.get("DP_API_KEY"),
        help="API key (default: $DP_API_KEY)",
    )
    keys_sub = keys_parser.add_subparsers(dest="keys_action", help="Key actions")

    create_parser = keys_sub.add_parser("create", help="Create a new API key")
    create_parser.add_argument(
        "--name", default="Default", help="Key name (default: Default)"
    )

    keys_sub.add_parser("list", help="List active API keys")

    revoke_parser = keys_sub.add_parser("revoke", help="Revoke an API key")
    revoke_parser.add_argument("key_id", help="UUID of the key to revoke")

    args = parser.parse_args()

    if args.command == "parse":
        cmd_parse(args)
    elif args.command == "share":
        cmd_share(args)
    elif args.command == "keys":
        if not args.keys_action:
            keys_parser.print_help()
            sys.exit(1)
        cmd_keys(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
