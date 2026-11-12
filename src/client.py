import sys, time, statistics, requests
PORT = sys.argv[1] if len(sys.argv) > 1 else '8100'                  # 8100 : H2O, 8101 : FLAML
URL = f'http://127.0.0.1:{PORT}/invocations'
CORPS = {'dataframe_records': [{'montant': 8500.0, 'anciennete': 3,
                                'freq_24h': 9, 'nuit': 1}]}
r = requests.post(URL, json=CORPS, timeout=10)
print('reponse :', r.status_code, r.json())
lat = []
for _ in range(50):                                                   # 50 appels pour mesurer
    t = time.perf_counter()
    requests.post(URL, json=CORPS, timeout=10)
    lat.append((time.perf_counter() - t) * 1000)
lat.sort()
print('mediane', round(statistics.median(lat), 1), 'ms')
print('p95    ', round(lat[int(0.95 * len(lat))], 1), 'ms')
