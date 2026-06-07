# GitHub ↔ Replit Sync Guide

This project uses **`sync_to_github.py`** to push changes from Replit to GitHub,
because Replit's environment has a grafted/shallow git history that prevents normal
`git push`.

## Quick Start

Run the **"Sync to GitHub"** workflow from the Replit run panel, or from the shell:

```bash
python3 sync_to_github.py
```

This pushes all tracked project files to `pmcgehee21/BookStoreApp@main` with an
auto-generated timestamped commit message.

**Requirement:** The `GITHUB_TOKEN` secret must be set in Replit Secrets (repo scope).

---

## Usage Options

```bash
# Push all tracked files (default)
python3 sync_to_github.py

# Push specific files only
python3 sync_to_github.py --files backend/app.py frontend/app.js

# Custom commit message
python3 sync_to_github.py --message "Fix order total calculation"

# Preview what would be pushed (no changes made)
python3 sync_to_github.py --dry-run
```

---

## Tracked Files

`sync_to_github.py` pushes these files by default:

| File | Purpose |
|------|---------|
| `.replit` | Replit environment config |
| `main.py` / `pyproject.toml` | Python project files |
| `sync_to_github.py` | This sync script |
| `GITHUB_SYNC.md` | This guide |
| `backend/app.py` | Flask app entry point |
| `backend/models.py` | Database models |
| `backend/database.py` | DB configuration |
| `backend/seed.py` | Data seeding utility |
| `backend/backup.py` | Backup utility |
| `backend/requirements.txt` | Python dependencies |
| `backend/books.csv` | Book catalog data |
| `backend/routes/*.py` | API route handlers |
| `frontend/index.html` | Frontend HTML |
| `frontend/app.js` | Frontend JavaScript |
| `frontend/style.css` | Frontend styles |

To add a new file to the default sync list, add its path to the `TRACKED_FILES`
list in `sync_to_github.py`.

---

## Pulling GitHub → Replit

To pull the latest version of specific files from GitHub into Replit:

```bash
python3 << 'PYEOF'
import os, base64, json, urllib.request

OWNER = "pmcgehee21"
REPO  = "BookStoreApp"
BRANCH = "main"
TOKEN  = os.environ["GITHUB_TOKEN"]

BASE = "/home/runner/workspace"
headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

def pull_file(filepath):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{filepath}?ref={BRANCH}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    content = base64.b64decode(data["content"])
    full_path = os.path.join(BASE, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "wb") as f:
        f.write(content)
    print(f"  OK  {filepath}")

FILES_TO_PULL = [
    "backend/app.py",
    # add more files here...
]

for f in FILES_TO_PULL:
    pull_file(f)
PYEOF
```

---

## Checking GitHub Status

```bash
python3 << 'PYEOF'
import os, json, urllib.request

OWNER = "pmcgehee21"; REPO = "BookStoreApp"
TOKEN = os.environ["GITHUB_TOKEN"]
headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
req = urllib.request.Request(
    f"https://api.github.com/repos/{OWNER}/{REPO}/commits?per_page=5", headers=headers)
with urllib.request.urlopen(req) as resp:
    for c in json.loads(resp.read()):
        print(c["sha"][:7], c["commit"]["message"][:70])
PYEOF
```

---

## Why Not `git push`?

The Replit environment has a grafted/shallow git history (`grafted` tag visible in
`git log`). Some commit objects are incomplete, causing:

```
error: Could not read <sha>
error: could not parse commit <sha>
```

The GitHub REST API works around this by treating each file as an independent update —
no git object graph required.

---

## Token Management

- `GITHUB_TOKEN` in Replit Secrets must have **`repo` scope** (or fine-grained
  "Contents: Read and write" + "Metadata: Read" for least privilege).
- To rotate: create a new token at https://github.com/settings/tokens, then update
  `GITHUB_TOKEN` in the Replit Secrets panel.
