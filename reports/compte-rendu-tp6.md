# TP 6 — Créer et déployer un modèle via une plateforme AutoML : compte rendu

Environnement : Windows 11, Java Temurin 17.0.20, Python 3.13, H2O-3 3.46.0.12, MLflow 3.18.0, FLAML 2.7.0, LightGBM 4.7.0.

> **Port MLflow** : sur ce poste, le port 5000 est déjà pris par une autre application. Le serveur MLflow a donc été lancé sur le port **5001** (`mlflow server --host 127.0.0.1 --port 5001 --backend-store-uri sqlite:///mlflow.db`) et les scripts lisent `MLFLOW_TRACKING_URI` (valeur par défaut `http://127.0.0.1:5000`, comme dans l'énoncé). Avant chaque script : `$env:MLFLOW_TRACKING_URI = "http://127.0.0.1:5001"`.

## Fichiers produits

| Fichier | Rôle |
|---|---|
| `src/h2o_automl.py` | AutoML H2O (10 modèles, graine 42, sans Deep Learning), enregistrement de `fraude-h2o` |
| `src/flaml_automl.py` | AutoML FLAML (25 essais, graine 42), enregistrement de `fraude-flaml` |
| `src/promouvoir.py` | pose l'alias `production` sur la dernière version (`python src/promouvoir.py fraude-h2o` ou `fraude-flaml`) — c'est le bloc `@' ... '@ \| python -` de l'énoncé, mis dans un fichier |
| `src/client.py` | client HTTP : une prédiction puis 50 appels chronométrés |
| `reports/tp6_comparaison.md` | tableau comparatif complété |
| `reports/tp6_sorties.txt` | sorties réelles de toutes les étapes, y compris l'erreur de l'étape 7 |

## Résultats mesurés

| Étape | Résultat |
|---|---|
| H2O AutoML | projet `AutoML_1_20261112_23749`, modèle retenu **StackedEnsemble_AllModels**, AUC (CV) 0.9870, **F1 test = 0.8623** |
| Registre MLflow | `fraude-h2o` v1 et `fraude-flaml` v1, alias `production` sur les deux (expérience `tp6-automl-deploiement`) |
| Endpoint H2O (port 8100) | `{'predict': 1, 'p0': 1.2e-05, 'p1': 0.99999}` — médiane **61 à 65 ms**, p95 81 à 123 ms (3 séries) |
| FLAML | modèle retenu **lgbm**, **F1 test = 0.8359** (identique à l'énoncé) |
| Endpoint FLAML (port 8101) | `{'predictions': [1]}` — médiane **10 à 12 ms**, p95 14 à 17 ms |
| Panne contrôlée | après redémarrage d'H2O : **400** `H2OKeyNotFoundArgumentException: Object 'StackedEnsemble_AllModels_1_AutoML_1_20261112_23749' not found`. Port 8101 : réponse normale. Après relance de `mlflow models serve` : 200 |
| Tailles | H2O 5.1 Mo · FLAML 43 Ko · forêt du pipeline 16.1 Mo |

### Écarts avec l'énoncé

- **Pas de XGBoost dans H2O** : le journal affiche « XGBoost is not available; skipping it ». L'extension XGBoost d'H2O-3 n'est pas fournie sous Windows. Les 10 modèles de base sont donc des GBM, GLM, DRF et XRT ; le leaderboard diffère de celui de l'énoncé et le F1 du Stacked Ensemble est **0.8623** au lieu de 0.8464. Conséquence pour l'étape 3 : la fiche à ouvrir dans H2O Flow est **GBM_1_...** (le meilleur modèle simple), pas XGBoost_2.
- **Latence H2O plus basse que dans l'énoncé** (≈ 63 ms au lieu de 260–450 ms) ; seule la première série juste après un redémarrage atteint 271 ms (chargement à froid). L'écart avec FLAML est donc d'environ **×5 à ×6**, pas ×50, mais l'ordre de grandeur reste nettement en faveur de FLAML.

## Étape 3 — H2O Flow (à compléter avec vos captures)

Ouvrir http://127.0.0.1:54321, puis `getLeaderboard "AutoML_1_xxx@@fraude"` (Ctrl+Entrée).

> ⚠️ Après la panne de l'étape 7, H2O a été redémarré : le projet AutoML a disparu de sa mémoire. Pour faire les captures, relancez `python src/h2o_automl.py` (nouveau projet `AutoML_x_...`, version 2 de `fraude-h2o` ; les scores sont les mêmes).

Points attendus :
- EVENT LOG : validation **5-fold cross-validation**, **Build control seed: 42**.
- VARIABLE IMPORTANCES : `montant` loin devant, puis `anciennete`, `freq_24h`, `nuit`.
- Matrice **TRAINING** nettement plus optimiste que **CROSS VALIDATION** : le modèle est évalué sur les lignes qu'il a apprises ; la validation croisée l'évalue sur des plis qu'il n'a pas vus.

## Réponses aux questions

**1. Stacked Ensemble.** C'est un modèle à deux niveaux : les modèles de base (ici les GBM, GLM, DRF, XRT de l'AutoML) produisent chacun une probabilité de fraude, puis un méta-modèle (un GLM chez H2O) apprend à combiner ces probabilités, à partir des prédictions de validation croisée. Il gagne quelques millièmes d'AUC (0.9870 contre 0.9856 pour GBM_1). Pour un client dont la carte a été bloquée, l'explication devient difficile : la décision dépend de dix modèles et des poids du méta-modèle ; on ne peut plus dire simplement « le montant et l'heure ont pesé tant ». Il faudrait des méthodes post-hoc (SHAP sur l'ensemble, coûteuses et approximatives). Dans un contexte réglementé (banque, droit à l'explication), c'est un vrai handicap.

**2. `max_models`, `seed`, pas de Deep Learning.** Pour la **reproductibilité** : avec un budget en nombre de modèles et une graine, deux exécutions entraînent exactement les mêmes modèles et donnent le même classement. Deep Learning est exclu car il est non déterministe par défaut (calcul multi-thread Hogwild!). Avec `max_runtime_secs=60`, le nombre de modèles entraînés dépend de la vitesse et de la charge de la machine : deux exécutions (ou deux postes) peuvent produire des leaderboards différents et un leader différent — « deux exécutions, deux scores ». On perd aussi la possibilité de comparer honnêtement deux versions du jeu de données.

**3. Latence.** Le service MLflow d'un modèle H2O n'est qu'un relais : à chaque appel, il convertit le JSON en DataFrame pandas, l'envoie au serveur Java H2O en HTTP (création d'un `H2OFrame`, donc un parse côté JVM), lance un job de prédiction sur 10 modèles + le méta-modèle, puis rapatrie le résultat et le reconvertit. Le modèle FLAML est un objet LightGBM en mémoire du même processus Python : un appel direct, sans saut réseau ni sérialisation. Mesuré ici : ≈ 63 ms contre ≈ 11 ms (×5 à ×6 ; ×50 dans l'énoncé, selon le poste). Pour autoriser un paiement en temps réel, où le budget de latence est de quelques dizaines de millisecondes au total, je choisirais **FLAML** : même décision, F1 très proche, latence et p95 bien plus faibles et stables.

**4. « Object ... not found ».** Le service H2O n'est pas autonome : le modèle vit dans la **mémoire du serveur H2O** (JVM), pas dans le processus qui sert l'API. L'endpoint ne garde qu'une référence (l'identifiant du modèle). Quand H2O redémarre, la mémoire est vidée, la référence pointe dans le vide, et l'endpoint reste « vivant » (le `/ping` répond) tout en échouant sur chaque prédiction. Il y a deux composants à état, couplés, qui peuvent tomber séparément. Détection automatique (TP 7) : une **sonde de santé applicative** qui envoie périodiquement une vraie transaction de test sur `/invocations` (et non seulement `/ping`), plus le suivi du **taux de réponses 4xx/5xx** et de la latence dans le monitoring (Prometheus/Grafana), avec alerte et redémarrage automatique du service de prédiction (readiness/liveness probe).

**5. Quel modèle en production ?** Le modèle manuel du TP 3 a le meilleur F1 (0.8669), mais l'écart avec H2O (0.8623) et FLAML (0.8359) doit être jugé avec d'autres critères : **latence** et p95 (paiement temps réel), **dépendances** et robustesse (pas de JVM ni de serveur à état), **taille** (43 Ko pour FLAML contre 16 Mo pour la forêt), **explicabilité** (un seul modèle d'arbres, importances et SHAP), **reproductibilité** et coût de maintenance. Je déploierais la forêt du TP 3 ou le LightGBM de FLAML — pas le Stacked Ensemble H2O — en choisissant entre les deux selon le coût métier d'une fraude manquée (rappel) face à une fausse alerte. Le F1 seul ne suffit pas : il faut aussi fixer un seuil de décision adapté.

**6. Reconstruire le modèle H2O dans deux ans.** Le format binaire H2O n'est lisible que par la même version d'H2O, et l'export MOJO autonome est réservé à l'édition commerciale. Il faut donc conserver : le **script** `src/h2o_automl.py` (versionné dans Git), les **données exactes** versionnées avec **DVC** (`data/transactions.csv.dvc`), le découpage (`random_state=42`, `test_size=0.25`), les **paramètres de l'AutoML** (`max_models=10`, `seed=42`, `exclude_algos=['DeepLearning']`, `sort_metric='AUC'`), la **version exacte d'H2O (3.46.0.12) et de Java (17)**, l'OS (le contenu du leaderboard dépend de la disponibilité de XGBoost : absent sous Windows), les versions des bibliothèques Python (`pip freeze`), et l'artefact binaire lui-même dans le registre MLflow.

## Livrables restant à faire à la main

- [ ] Captures H2O Flow : leaderboard + fiche de GBM_1 avec VARIABLE IMPORTANCES → `reports/captures/`
- [ ] Capture du registre MLflow (http://127.0.0.1:5001/#/models) montrant `fraude-h2o` et `fraude-flaml` avec l'alias `production`
