# --- make parent folder importable ---
import sys, os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# now imports work no matter where Render runs from
from watchers import secrets_watcher

if __name__ == "__main__":
    # lance directement le watcher (boucle interne dans secrets_watcher)
    secrets_watcher.main()
