import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from interpret.glassbox import ExplainableBoostingClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import partial_dependence
from sklearn.metrics import f1_score
from sklearn.tree import DecisionTreeClassifier
from xai_commun import m, Xtr, Xte, ytr, yte, CAS
# 1. EBM : une courbe par variable, explication exacte
ebm = ExplainableBoostingClassifier(interactions=0, random_state=42).fit(Xtr, ytr)
print('EBM F1 =', round(f1_score(yte, ebm.predict(Xte)), 4))
loc = ebm.explain_local(CAS).data(0)
print('Mme Benali :', {k: round(float(v), 2) for k, v in zip(loc['names'], loc['scores'])},
      '+ constante', round(ebm.intercept_[0], 2), '-> P =', round(ebm.predict_proba(CAS)[0, 1], 3))
# 2. Boosting avec et sans contrainte de monotonie (montant +, anciennete -, freq +, nuit +)
fig, ax = plt.subplots(figsize=(7, 4))
for cst, lab in [(None, 'sans contrainte'), ([1, -1, 1, 1], 'avec contrainte')]:
    h = HistGradientBoostingClassifier(random_state=0, monotonic_cst=cst).fit(Xtr, ytr)
    print(f'boosting {lab:16s} F1 = {f1_score(yte, h.predict(Xte)):.4f}')
    pd_ = partial_dependence(h, Xte.astype(float), ['anciennete'], method='brute',
                             response_method='predict_proba', grid_resolution=60)
    ax.plot(pd_['grid_values'][0], pd_['average'][0], label=lab)
ax.set_xlabel('anciennete (mois)'); ax.set_ylabel('P(fraude) moyenne'); ax.legend()
plt.tight_layout(); plt.savefig('reports/monotonie.png', dpi=120)
# 3. Substitut : un arbre court qui imite la foret
pf_tr, pf_te = m.predict(Xtr), m.predict(Xte)
for p in [3, 5]:
    s = DecisionTreeClassifier(max_depth=p, random_state=0).fit(Xtr, pf_tr)
    acc = (s.predict(Xte) == pf_te).mean(); accf = (s.predict(Xte)[pf_te == 1] == 1).mean()
    print(f'substitut prof. {p} : accord {acc:.1%}, accord sur les fraudes de la foret {accf:.1%}')
