import numpy as np
from xai_commun import m, CAS
p = lambda d: m.predict_proba(d)[0, 1]
print('situation reelle : P =', round(p(CAS), 3))
c = CAS.copy(); c['nuit'] = 0
print('meme paiement de jour : P =', round(p(c), 3))
c = CAS.copy()
for v in np.arange(1800, 0, -10): # on baisse le montant pas a pas
    c['montant'] = v
    if p(c) < 0.5: print(f'montant <= {v} MAD : P =', round(p(c), 3)); break
c = CAS.copy()
for a in range(30, 121): # on augmente l'anciennete
    c['anciennete'] = a
    if p(c) < 0.5: print(f'anciennete >= {a} mois : P =', round(p(c), 3)); break
