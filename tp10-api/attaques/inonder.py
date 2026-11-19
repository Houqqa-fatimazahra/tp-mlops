"""Envoie N requetes le plus vite possible et compte les codes HTTP recus."""
import collections, sys, time

import requests

URL, CLE, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
CORPS = {"montant": 1800, "anciennete": 30, "freq_24h": 4, "nuit": 1}
session = requests.Session()
codes = collections.Counter()
debut = time.perf_counter()
for _ in range(N):
    r = session.post(URL, json=CORPS, headers={"X-API-Key": CLE},
                     timeout=5, verify="certs/client.pem")
    codes[r.status_code] += 1
duree = time.perf_counter() - debut
print(f"{N} requetes en {duree:.1f} s")
for code, nombre in sorted(codes.items()):
    print(f"  HTTP {code} : {nombre}")
