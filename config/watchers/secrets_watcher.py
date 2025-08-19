import os, time, json, requests, yaml, re

# 🎯 Signatures de secrets connus
PATTERNS = {
    "aws_access_key_id": re.compile(r'AKIA[0-9A-Z]{16}'),
    "stripe_live": re.compile(r'sk_live_[0-9a-zA-Z]{10,}'),
    "generic_secret": re.compile(r'(?i)(secret|token|apikey|api_key)[^\n]{0,20}[:=][^\n]{10,}')
}
SUSPICIOUS_PATHS = [".env", "serviceAccountKey.json", "config.yml", ".npmrc", "credentials"]

def score_snippet(path, text):
    score = 0
    if any(p in path.lower() for p in SUSPICIOUS_PATHS): score += 2
    for _, pat in PATTERNS.items():
        if pat.search(text): score += 2
    return score

def gh_headers():
    h = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token: h["Authorization"] = f"Bearer {token}"
    return h

def scan_commit(repo_full, sha):
    url = f"https://api.github.com/repos/{repo_full}/commits/{sha}"
    r = requests.get(url, headers=gh_headers(), timeout=20)
    if r.status_code != 200: return []
    out = []
    for f in r.json().get("files", []):
        filename = f.get("filename","")
        patch = f.get("patch") or ""
        if not patch: continue
        added = "\n".join([ln[1:] for ln in patch.splitlines() if ln.startswith("+")])
        if score_snippet(filename, added) >= 3:
            out.append({
                "type":"secret_candidate",
                "repo": repo_full, "sha": sha, "path": filename,
                "snippet_preview": added[:300]
            })
    return out

def watch_user_or_org(name):
    url = f"https://api.github.com/users/{name}/events/public"
    r = requests.get(url, headers=gh_headers(), timeout=20)
    if r.status_code != 200: return []
    findings = []
    for ev in r.json():
        if ev.get("type") != "PushEvent": continue
        repo = ev.get("repo",{}).get("name")
        for c in ev.get("payload",{}).get("commits",[]):
            findings += scan_commit(repo, c.get("sha"))
    return findings

def main():
    with open("config/scope.yaml","r",encoding="utf-8") as f:
        scope = yaml.safe_load(f)
    orgs = scope.get("github",{}).get("orgs",[])
    poll = int(os.getenv("POLL_INTERVAL_SECONDS","120"))
    while True:
        for org in orgs:
            try:
                hits = watch_user_or_org(org)
                for h in hits: print(json.dumps(h, ensure_ascii=False))
            except Exception as e:
                print(json.dumps({"error": str(e), "org": org}))
        time.sleep(poll)

if __name__ == "__main__":
    main()
