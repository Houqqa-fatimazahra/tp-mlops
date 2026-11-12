import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.inspection import PartialDependenceDisplay, partial_dependence
from xai_commun import m, Xte
Xf = Xte.astype(float) # le PDP refuse les colonnes entieres
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
PartialDependenceDisplay.from_estimator(m, Xf, ['montant', 'anciennete'], kind='both',
                                        subsample=60, random_state=0, ax=ax)
plt.tight_layout(); plt.savefig('reports/pdp_ice.png', dpi=120)
for v in ['montant', 'anciennete']:
    moy = partial_dependence(m, Xf, [v], kind='average')['average'][0]
    print(f'{v:11s} PDP de {moy.min():.3f} a {moy.max():.3f}')
