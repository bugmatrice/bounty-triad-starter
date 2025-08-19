import time
from watchers.secrets_watcher import score_snippet

print("🚀 Shadow scanner lancé...")

# Exemple de boucle simple
while True:
    # Ici plus tard on scannera les repos / fichiers
    test = score_snippet("test.env", "aws_access_key_id=EXAMPLE123")
    if test > 0:
        print(f"[ALERTE] Secret trouvé avec score {test}")
    else:
        print("Rien trouvé, on continue...")

    time.sleep(10)  # pause de 10 secondes avant le prochain scan
