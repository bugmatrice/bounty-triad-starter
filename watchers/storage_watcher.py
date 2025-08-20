import json, requests, yaml

def s3_public(bucket: str) -> bool:
    try:
        r = requests.get(f"https://{bucket}.s3.amazonaws.com/", timeout=6)
        if r.status_code == 200 and "<ListBucketResult" in r.text:
            return True
    except Exception:
        pass
    return False

def derive_s3_names(root: str, hints):
    base = root.replace(".", "-")
    names = {base}
    for h in hints:
        names.add(f"{h}-{base}")
        names.add(f"{base}-{h}")
    return sorted(names)

def run(scope: dict):
    roots = (scope.get("dns",{}) or {}).get("root_domains", [])
    hints = (scope.get("storage",{}) or {}).get("naming_hints", []) or ["cdn","assets","static","public","img"]
    for root in roots:
        for name in derive_s3_names(root, hints):
            if s3_public(name):
                print(json.dumps({
                    "type":"public_storage_candidate",
                    "provider":"aws_s3",
                    "bucket": name
                }))
