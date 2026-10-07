#!/usr/bin/env python3
"""
Fetch live KingOfLinks pages for verification against local HTML.

Rules:
- Live site uses .htm paths.
- Do not guess missing data.
- Use this only to retrieve the exact live page corresponding to the local file.
- Keep page/file matching strict.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request


BASE_URL = "http://kingoflinks.net"
USER_AGENT = "Mozilla/5.0"


def normalize_live_path(path: str) -> str:
    """
    Convert a repo-style path to the live-site path format.

    Examples:
      Abdulmtalib/1.html -> Abdulmtalib/1.htm
      /Abdulmtalib/1.htm -> Abdulmtalib/1.htm
    """
    path = path.strip().lstrip("/")
    if path.lower().endswith(".html"):
        path = path[:-5] + ".htm"
    return path


def fetch_live(path: str, timeout: int = 15) -> tuple[str, bytes]:
    """
    Fetch a live page from kingoflinks.net via urllib.

    Returns:
        (url, raw_bytes)

    The raw bytes are returned unchanged so no content is lost through an
    incorrect text-decoding assumption.
    """
    live_path = normalize_live_path(path)
    url = f"{BASE_URL}/{live_path}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    with urllib.request.urlopen(req, timeout=timeout) as response:
        return url, response.read()


def decode_best_effort(raw: bytes) -> tuple[str, str]:
    """
    Decode for inspection only.

    Tries Windows-1256 first because legacy Arabic pages commonly use it,
    then UTF-8, then latin-1 as a lossless byte-preserving fallback.
    Returns (encoding_name, text).
    """
    for encoding in ("windows-1256", "utf-8", "latin-1"):
        try:
            return encoding, raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return "latin-1", raw.decode("latin-1")


def extract_numbers(text: str) -> list[str]:
    """Extract ASCII digit sequences for strict block/reference matching."""
    return re.findall(r"\d+", text)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch and inspect a live kingoflinks.net page."
    )
    parser.add_argument(
        "path",
        help="Repo or live path, e.g. Abdulmtalib/1.html or Abdulmtalib/1.htm",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="HTTP timeout in seconds (default: 15)",
    )
    parser.add_argument(
        "--raw-output",
        help="Optional file path to save the exact raw response bytes",
    )
    parser.add_argument(
        "--numbers-only",
        action="store_true",
        help="Print only extracted ASCII number sequences",
    )
    args = parser.parse_args()

    try:
        url, raw = fetch_live(args.path, timeout=args.timeout)
    except urllib.error.HTTPError as exc:
        print(f"HTTP error {exc.code} for {exc.url}", file=sys.stderr)
        return 2
    except urllib.error.URLError as exc:
        print(f"URL error: {exc.reason}", file=sys.stderr)
        return 3
    except TimeoutError:
        print("Request timed out", file=sys.stderr)
        return 4

    if args.raw_output:
        with open(args.raw_output, "wb") as f:
            f.write(raw)

    encoding, text = decode_best_effort(raw)

    if args.numbers_only:
        print("\n".join(extract_numbers(text)))
        return 0

    print(f"URL: {url}")
    print(f"Bytes: {len(raw)}")
    print(f"Inspection encoding: {encoding}")
    print("-" * 80)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
