"""Provoque une erreur et resume ce que la reponse revele a un attaquant."""
import re, sys

import requests

URL, CLE = sys.argv[1], sys.argv[2]
corps = {"montant": "abc", "anciennete": 30, "freq_24h": 4, "nuit": 1}
r = requests.post(URL, json=corps, headers={"X-API-Key": CLE},
                  timeout=5, verify="certs/client.pem")
lignes = r.text.splitlines()
print(f"HTTP {r.status_code} - {len(r.text)} caracteres de reponse")
fichiers = [l for l in lignes if l.strip().startswith('File "') and "site-packages" not in l]
for l in fichiers:
    if "/api/" in l or "\\api\\" in l:
        i = lignes.index(l)
        print("chemin et ligne du code :", l.strip())
        print("instruction fautive     :", lignes[i + 1].strip())
libs = sorted(set(re.findall(r"site-packages[/\\](\w+)", r.text)))
if libs:
    print("bibliotheques visibles  :", ", ".join(libs))
    print("derniere ligne          :", lignes[-1])
else:
    print("reponse                 :", r.text[:150])
