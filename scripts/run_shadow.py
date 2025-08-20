# --- make project importable whatever the working dir ---
import sys, os, time, yaml, importlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# load scope once (reload on file change if you veux plus tard)
with open(os.path.join(PROJECT_ROOT, "config", "scope.yaml"), "r", encoding="utf-8") as f:
    SCOPE = yaml.safe_load(f)

WATCHER_MODULES = [
    "watchers.secrets_watcher",
    "watchers.dns_takeover_watcher",
    "watchers.storage_watcher",
]

WATCHERS = []
for m in WATCHER_MODULES:
    try:
        mod = importlib.import_module(m)
        if hasattr(mod, "run"):
            WATCHERS.append(mod)
            print(f"🔍 Loaded {m}")
    except Exception as e:
        print(f"❌ Load error {m}: {e}")

print("🚀 Radar running…")

POLL = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
while True:
    for w in WATCHERS:
        try:
            w.run(SCOPE)  # each run = one sweep; keep it fast
        except Exception as e:
            print(f"❌ Watcher error {w.__name__}: {e}")
    time.sleep(POLL)
