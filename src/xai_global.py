import numpy as np, pandas as pd, shap
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from xai_commun import m, Xte
Xs = Xte.sample(400, random_state=0)
sv = shap.TreeExplainer(m)(Xs)[:, :, 1] # 400 explications, classe fraude
imp = pd.Series(np.abs(sv.values).mean(0), index=Xs.columns)
print(imp.sort_values(ascending=False).round(4).to_string())
shap.plots.beeswarm(sv, show=False)
plt.tight_layout(); plt.savefig('reports/shap_global.png', dpi=120); plt.close('all')
plt.scatter(Xs['montant'], sv[:, 'montant'].values, c=Xs['nuit'], cmap='coolwarm', s=12)
plt.xscale('log'); plt.xlabel('montant (MAD)'); plt.ylabel('contribution SHAP du montant')
plt.colorbar(label='nuit'); plt.tight_layout(); plt.savefig('reports/shap_montant.png', dpi=120)
print('graphiques ecrits')
