# GitHub ↔ Replit Sync Guide

This project uses **manual sync via the GitHub REST API** because Replit's environment
has a grafted/shallow git history that prevents normal `git push` / `git pull`.

## Current Status

- GitHub repo: `https://github.com/pmcgehee21/BookStoreApp`
- Branch: `main`
- Secret required: `GITHUB_TOKEN` (repo scope) — stored in Replit Secrets

---

## Pushing Replit → GitHub

Use the script below any time you want to push local file changes to GitHub.
It reads each file, fetches its current SHA from GitHub, and updates it via the API.

```bash
python3 << 'PYEOF'
import os, base64, json
import urllib.request, urllib.error

OWNER = "pmcgehee21"
REPO  = "BookStoreApp"
BRANCH = "main"
TOKEN  = os.environ["GITHUB_TOKEN"]   # set in Replit Secrets

BASE = "/home/runner/workspace"
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}

def get_sha(filepath):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{filepath}?ref={BRANCH}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()).get("sha")
    except urllib.error.HTTPError as e:
        return None if e.code == 404 else (_ for _ in ()).throw(e)

def push_file(filepath, message):
    with open(os.path.join(BASE, filepath), "rb") as f:
        content = base64.b64encode(f.read()).decode()
    body = {"message": message, "content": content, "branch": BRANCH}
    sha = get_sha(filepath)
    if sha:
        body["sha"] = sha
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{filepath}"
    req = urllib.request.Request(url, json.dumps(body).encode(), headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✅ {filepath}")
    except urllib.error.HTTPError as e:
        print(f"❌ {filepath}: {json.loads(e.read()).get('message')}")

# Edit this list to include files you want to push
FILES_TO_PUSH = [
    "backend/app.py",
    # add more files here...
]
COMMIT_MESSAGE = "Your commit message here"

for f in FILES_TO_PUSH:
    push_file(f, COMMIT_MESSAGE)
PYEOF
```

---

## Pulling GitHub → Replit

Use this script to pull the latest version of specific files from GitHub into Replit.

```bash
python3 << 'PYEOF'
import os, base64, json
import urllib.request

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
    print(f"✅ {filepath}")

# Edit this list to include files you want to pull
FILES_TO_PULL = [
    "backend/app.py",
    # add more files here...
]

for f in FILES_TO_PULL:
    pull_file(f)
PYEOF
```

---

## Checking Sync Status

To see if Replit is ahead of or behind GitHub:

```bash
# Show latest 5 commits on GitHub
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

## Why not `git push`?

The Replit environment has a grafted/shallow git history (`grafted` tag visible in
`git log`). This means some commit objects are incomplete, causing:

```
error: Could not read <sha>
error: could not parse commit <sha>
```

The GitHub REST API approach works around this by treating each file as an independent
update — no git object graph required.

---

## Keeping the Token Fresh

- The `GITHUB_TOKEN` secret in Replit Secrets must have **`repo` scope**.
- Classic tokens expire based on the expiry you set when creating them.
- To rotate: create a new token at https://github.com/settings/tokens, then update
  the `GITHUB_TOKEN` secret in Replit's Secrets panel.
