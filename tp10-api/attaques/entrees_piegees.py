"""Envoie des donnees absurdes ou malformees et affiche la reaction de l'API."""
import sys

import requests

URL, CLE = sys.argv[1], sys.argv[2]
BENALI = {"montant": 1800, "anciennete": 30, "freq_24h": 4, "nuit": 1}
PIEGES = [("montant negatif", dict(BENALI, montant=-5000)),
          ("nuit = 7", dict(BENALI, nuit=7)),
          ("montant gigantesque", dict(BENALI, montant=1e300)),
          ("champ en plus", dict(BENALI, role="admin")),
          ("montant texte", dict(BENALI, montant="abc")),
          ("champ manquant", {"montant": 1800, "anciennete": 30, "freq_24h": 4})]

for nom, corps in PIEGES:
    r = requests.post(URL, json=corps, headers={"X-API-Key": CLE},
                      timeout=5, verify="certs/client.pem")
    print(f"{nom:20} -> {r.status_code}  {r.text[:56]}".replace("\n", " "))
