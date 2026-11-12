from lime.lime_tabular import LimeTabularExplainer
from xai_commun import m, X, Xtr, CAS
ex0 = LimeTabularExplainer(Xtr.values, feature_names=list(X.columns), mode='classification',
                           class_names=['legitime', 'fraude'], random_state=0)
print('regles :', [k for k, _ in ex0.explain_instance(CAS.values[0], m.predict_proba,
                                                      num_features=4).as_list()])
for n in [500, 2000]: # taille du voisinage
    print(f'--- {n} voisins montant nuit anciennete freq_24h')
    for graine in range(5): # 5 tirages : l'explication est-elle stable ?
        ex = LimeTabularExplainer(Xtr.values, feature_names=list(X.columns), mode='classification',
                                  class_names=['legitime', 'fraude'], random_state=graine)
        e = dict(ex.explain_instance(CAS.values[0], m.predict_proba, num_features=4,
                                     num_samples=n).as_list())
        w = [next(v for k, v in e.items() if col in k) for col in X.columns]
        print(f'graine {graine} {w[0]:+.3f} {w[3]:+.3f} {w[1]:+.3f} {w[2]:+.3f}')
