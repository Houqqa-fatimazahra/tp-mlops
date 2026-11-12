# TP 5 — Tableau comparatif

Jeu de données : `data/transactions.csv` (5 000 lignes, 568 fraudes, soit 11,4 %). Test sur 25 % des lignes (1 250, dont 142 fraudes).
Métrique : F1 de la classe 1 (fraude). Référence (régression logistique, `src/reference.py`) : F1 = 0.7407.

| Approche                | F1 cl. 1 | Temps humain | Temps machine        | Cout  | Explicabilite                                   | Export                     |
|-------------------------|----------|--------------|----------------------|-------|-------------------------------------------------|----------------------------|
| Manuel (TP 3)           | 0.8669   | ~2 h         | 5 min                | 0 MAD | totale (chaque choix est écrit dans le code)    | MLflow                     |
| FLAML 10 s              | 0.8514   | 5 min        | 10 s                 | 0 MAD | bonne (config + `reports/flaml.log`)            | MLflow                     |
| FLAML 60 s              | 0.8359   | 5 min        | 1 min                | 0 MAD | bonne                                           | MLflow                     |
| FLAML 120 s             | 0.8636   | 5 min        | 2 min                | 0 MAD | bonne                                           | MLflow                     |
| Orange, Grad. Boosting  | 0.837    | ~45 min      | quelques secondes    | 0 MAD | moyenne (réglages visibles dans le `.ows`, matrice de confusion, ROC) | `.pkcls` (pickle Orange) |
| KNIME, meilleur modele (GBT) | 0.844 | ~45 min     | quelques secondes    | 0 MAD | moyenne (réglages dans chaque nœud, Scorer)     | `.knwf`                    |
| KNIME, composant AutoML (XGBoost) | 0.843 | ~20 min     | plusieurs minutes    | 0 MAD | moyenne à faible (classement visible, détail du réglage enfoui dans le composant) | workflow de déploiement (`models/knime-automl`) |

> Les protocoles ne sont pas strictement identiques (partage non stratifié de scikit-learn pour FLAML, stratifié 75/25 dans Orange et KNIME, 80/20 dans le composant AutoML de KNIME) : un écart d'un ou deux centièmes de F1 n'est pas significatif.

## Observation sur FLAML

Le budget de 60 s a donné un F1 **plus faible** (0.8359) que le budget de 10 s (0.8514). FLAML a été lancé sans graine (`seed`) : la recherche n'est pas reproductible, et le modèle retenu sur la validation interne n'est pas forcément le meilleur sur le jeu de test. Le gain réel du budget reste faible : de 10 s à 120 s (12 fois plus de calcul), le F1 ne gagne qu'environ un centième. C'est le rendement décroissant du budget de calcul.

## Dans quel contexte recommander chaque approche ?

1. **Manuel** : modèle critique mis en production, où chaque choix doit être justifié et audité ; c'est le meilleur F1, mais le plus coûteux en temps humain.
2. **FLAML** : point de départ rapide pour un data scientist ; en quelques minutes on obtient un F1 proche du manuel, avec une trace complète (journal + MLflow) qui s'intègre au pipeline MLOps.
3. **Orange** : enseignement, exploration et prototypage par des non-développeurs ; très visuel (matrice, ROC), mais l'export `.pkcls` demande du code Python pour être servi.
4. **KNIME** : analystes métier qui construisent des traitements de données répétables ; plus explicite qu'Orange (Learner / Predictor séparés, exécution contrôlée), et industrialisable avec KNIME Business Hub (payant).
5. **Composant AutoML de KNIME** : obtenir sans code un bon modèle et un workflow de déploiement prêt à l'emploi, à condition d'accepter une recherche moins transparente et plus longue que FLAML.
