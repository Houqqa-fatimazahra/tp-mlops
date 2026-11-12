import numpy as np, pandas as pd
from fairlearn.metrics import MetricFrame, false_positive_rate, selection_rate
from sklearn.metrics import recall_score
from xai_commun import m, Xte, yte
rng = np.random.default_rng(7) # groupe A/B FICTIF, pour l'exercice
p_b = np.where(Xte['anciennete'] < 24, 0.75, 0.25) # B plus frequent chez les clients recents
groupe = pd.Series(np.where(rng.random(len(Xte)) < p_b, 'B', 'A'), index=Xte.index, name='groupe')
pred = m.predict(Xte) # le modele ne voit JAMAIS le groupe
mf = MetricFrame(metrics={'taux_alerte': selection_rate, 'fausses_alertes': false_positive_rate,
                          'rappel': recall_score}, y_true=yte, y_pred=pred, sensitive_features=groupe)
print(mf.by_group.round(4).to_string())
print('taux reel de fraude :', yte.groupby(groupe).mean().round(4).to_dict())
print('ecart entre groupes :', mf.difference().round(4).to_dict())
