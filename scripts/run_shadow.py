import os
import time
import yaml
from watchers import secrets_watcher

def load_scope():
    """Charge le scope depuis config/scope.yaml"""
    with open("config/scope.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    print("🚀 Shadow Scanner lancé...")

    scope = load_scope()
    print(f"📌 Scope chargé : {scope}")

    # Boucle infinie : scanner toutes les X secondes
    while True:
        try:
            secrets_watcher.scan_repo()
        except Exception as e:
            print(f"❌ Erreur: {e}")
        time.sleep(30)  # scanner toutes les 30 sec

if __name__ == "__main__":
    main()
