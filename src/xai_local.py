import shap
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from xai_commun import m, CAS
ex = shap.TreeExplainer(m) # exact et rapide pour les arbres
e = ex(CAS)[0, :, 1] # classe 1 = fraude
print('moyenne du modele :', round(e.base_values, 4))
for nom, c in sorted(zip(CAS.columns, e.values), key=lambda t: -abs(t[1])):
    print(f'{nom:11s} {c:+.4f}')
print('somme :', round(e.base_values + e.values.sum(), 4))
print('prediction :', round(m.predict_proba(CAS)[0, 1], 4))
shap.plots.waterfall(e, show=False)
plt.tight_layout(); plt.savefig('reports/shap_benali.png', dpi=120)
