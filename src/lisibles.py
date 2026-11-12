import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text
from xai_commun import m, X, Xtr, Xte, ytr, yte, CAS
def logm(d): # le montant agit par ordre de grandeur
    d = d.copy(); d['log_montant'] = np.log10(d.pop('montant')); return d
for nom, f in [('montant brut', lambda d: d), ('log(montant)', logm)]:
    lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(f(Xtr), ytr)
    print(f'logistique, {nom:12s} F1 = {f1_score(yte, lr.predict(f(Xte))):.4f}')
coef = pd.Series(lr[-1].coef_[0], index=logm(Xtr).columns)
print('coefficients standardises :', coef.round(2).to_dict())
brut = np.exp(coef / lr[0].scale_) # effet d'une unite, en multiplicateur de cote
print('cote x', round(brut['anciennete'], 3), 'par mois d\'anciennete ; x',
      round(brut['freq_24h'], 2), 'par transaction en 24 h')
for p in [2, 3, 4, 6, None]:
    t = DecisionTreeClassifier(max_depth=p, random_state=0).fit(Xtr, ytr)
    print(f'arbre profondeur {str(p):4s}: {t.get_n_leaves():3d} feuilles, F1 = '
          f'{f1_score(yte, t.predict(Xte)):.4f}')
t3 = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr)
print(export_text(t3, feature_names=list(X.columns), decimals=1))
print('Mme Benali : feuille', t3.apply(CAS)[0], '| P =', round(t3.predict_proba(CAS)[0, 1], 3))
print('foret : F1 =', round(f1_score(yte, m.predict(Xte)), 4))
