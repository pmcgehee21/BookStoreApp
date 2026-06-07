#!/usr/bin/env python3
"""
sync_to_github.py — Push tracked project files to GitHub.

Usage:
    python3 sync_to_github.py [--files file1 file2 ...] [--message "commit msg"]

By default it pushes all files listed in TRACKED_FILES with a timestamped
commit message. Requires the GITHUB_TOKEN environment variable (repo scope).
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

OWNER = "pmcgehee21"
REPO = "BookStoreApp"
BRANCH = "main"
BASE = os.path.dirname(os.path.abspath(__file__))

TRACKED_FILES = [
    "main.py",
    "pyproject.toml",
    "sync_to_github.py",
    "GITHUB_SYNC.md",
    "backend/app.py",
    "backend/models.py",
    "backend/database.py",
    "backend/seed.py",
    "backend/backup.py",
    "backend/requirements.txt",
    "backend/books.csv",
    "backend/routes/auth.py",
    "backend/routes/books.py",
    "backend/routes/orders.py",
    "backend/routes/feedback.py",
    "backend/routes/vendor_orders.py",
    "frontend/index.html",
    "frontend/app.js",
    "frontend/style.css",
]


def get_headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }


def get_remote_sha(filepath, headers):
    url = (
        f"https://api.github.com/repos/{OWNER}/{REPO}"
        f"/contents/{filepath}?ref={BRANCH}"
    )
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()).get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def push_file(filepath, message, headers, dry_run=False):
    full_path = os.path.join(BASE, filepath)
    if not os.path.exists(full_path):
        print(f"  SKIP  {filepath} (not found locally)")
        return None

    with open(full_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    sha = get_remote_sha(filepath, headers)
    body = {"message": message, "content": content, "branch": BRANCH}
    if sha:
        body["sha"] = sha

    if dry_run:
        action = "create" if sha is None else "update"
        print(f"  DRY   {filepath} ({action})")
        return True

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{filepath}"
    req = urllib.request.Request(
        url, json.dumps(body).encode(), headers, method="PUT"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"  OK    {filepath}")
            return True
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"  FAIL  {filepath}: {err.get('message', str(e))}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Push project files to GitHub.")
    parser.add_argument(
        "--files", nargs="+", metavar="FILE",
        help="Specific files to push (default: all TRACKED_FILES)",
    )
    parser.add_argument(
        "--message", "-m",
        default=None,
        help="Commit message (default: auto-generated with timestamp)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be pushed without making changes",
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN environment variable is not set.")
        print("  Add a GitHub Personal Access Token (repo scope) to Replit Secrets.")
        sys.exit(1)

    headers = get_headers(token)

    files_to_push = args.files if args.files else TRACKED_FILES
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    message = args.message or f"Sync from Replit — {timestamp}"

    mode = " (DRY RUN)" if args.dry_run else ""
    print(f"Pushing {len(files_to_push)} file(s) to {OWNER}/{REPO}@{BRANCH}{mode}")
    print(f"Commit message: {message}\n")

    ok = 0
    fail = 0
    for f in files_to_push:
        result = push_file(f, message, headers, dry_run=args.dry_run)
        if result is True:
            ok += 1
        elif result is False:
            fail += 1

    print(f"\nDone — {ok} pushed, {fail} failed" + (", (skipped not counted)" if ok + fail < len(files_to_push) else ""))
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
