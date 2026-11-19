"""Appelle l'API et affiche le code HTTP puis la reponse.
Exemples :
  python appel.py GET  http://localhost:8000/health
  python appel.py POST http://localhost:8000/v1/predict montant=abc
  python appel.py POST https://localhost:8443/v1/predict --cle MA_CLE
Le corps envoye est le dossier de Mme Benali ; champ=valeur le modifie."""
import sys

import requests

methode, url, args = sys.argv[1].upper(), sys.argv[2], sys.argv[3:]
entetes = {}
if "--cle" in args:                                   # cle d'API dans l'en-tete X-API-Key
    i = args.index("--cle")
    entetes["X-API-Key"] = args[i + 1]
    args = args[:i] + args[i + 2:]


def valeur(texte):                                    # "1800" -> 1800, "abc" -> "abc"
    for conversion in (int, float):
        try:
            return conversion(texte)
        except ValueError:
            pass
    return texte


corps = {"montant": 1800, "anciennete": 30, "freq_24h": 4, "nuit": 1}
for a in args:
    champ, texte = a.split("=", 1)
    corps[champ] = valeur(texte)

r = requests.request(methode, url, headers=entetes, timeout=10, verify="certs/client.pem",
                     json=corps if methode == "POST" else None)
print(r.status_code, r.reason)
print(r.text[:400])
