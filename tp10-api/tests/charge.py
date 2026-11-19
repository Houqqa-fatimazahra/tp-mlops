"""Envoie N requetes avec C clients simultanes et affiche la latence."""
import concurrent.futures as cf, statistics, sys, time, requests

URL = sys.argv[1]
N, C = int(sys.argv[2]), int(sys.argv[3])
H = {"X-API-Key": sys.argv[4]} if len(sys.argv) > 4 else {}
CORPS = {"montant": 1800, "anciennete": 30, "freq_24h": 4, "nuit": 1}

def une():
    t = time.perf_counter()
    requests.post(URL, json=CORPS, headers=H, timeout=30).raise_for_status()
    return (time.perf_counter() - t) * 1000

debut = time.perf_counter()
with cf.ThreadPoolExecutor(C) as ex:
    lat = sorted(ex.map(lambda _: une(), range(N)))
total = time.perf_counter() - debut
print(f"{N} requetes, {C} clients : {N / total:.0f} req/s, "
      f"mediane {statistics.median(lat):.1f} ms, p95 {lat[int(0.95 * N)]:.1f} ms")
