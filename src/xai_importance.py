import pandas as pd
from sklearn.inspection import permutation_importance
from xai_commun import m, X, Xte, yte, CAS
print('P(fraude) Mme Benali :', round(m.predict_proba(CAS)[0, 1], 4))
r = permutation_importance(m, Xte, yte, scoring='f1', n_repeats=10, random_state=0)
t = pd.DataFrame({'MDI (foret)': m.feature_importances_, 'permutation': r.importances_mean,
                  'ecart-type': r.importances_std}, index=X.columns).round(3)
print(t.sort_values('permutation', ascending=False).to_string())
