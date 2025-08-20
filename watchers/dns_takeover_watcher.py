import os, json, socket, yaml, time
import dns.resolver
import requests

FINGERPRINTS = {
    "heroku": ["no such app", "heroku | error", "no such app id"],
    "vercel": ["vercel 404", "project not found", "there's nothing here"],
    "github_pages": ["there isn't a github pages site here", "404 not found"],
    "cloudfront": ["cloudfront", "bad request", "403 ERROR The request could not be satisfied".lower()],
    "azure": ["web app not found", "azurewebsites.net"],
    "fastly": ["fastly error: unknown domain"],
    "readme": ["project not found", "site not found"],
}

COMMON_HINTS = ["www","blog","app","api","cdn","static","img","dev","staging","test"]

def resolve_cname(host):
    try:
        ans = dns.resolver.resolve(host, 'CNAME')
        return [str(r.target).rstrip('.') for r in ans]
    except Exception:
        return []

def http_body(host):
    try:
        r = requests.get(f"http://{host}", timeout=6)
        return r.text.lower()
    except Exception:
        try:
            r = requests.get(f"https://{host}", timeout=6, verify=False)
            return r.text.lower()
        except Exception:
            return ""

def run(scope: dict):
    roots = (scope.get("dns",{}) or {}).get("root_domains", [])
    hints = list(set(((scope.get("dns",{}) or {}).get("wordlist_hint", []) or []) + COMMON_HINTS))
    for root in roots:
        candidates = {root} | {f"{h}.{root}" for h in hints}
        for host in candidates:
            cnames = resolve_cname(host)
            if not cnames: 
                continue
            body = http_body(host)
            for prov, phrases in FINGERPRINTS.items():
                if any(p in body for p in phrases):
                    print(json.dumps({
                        "type":"potential_takeover",
                        "host": host,
                        "cname": cnames,
                        "provider": prov,
                        "evidence": "fingerprint_phrase_match"
                    }))
