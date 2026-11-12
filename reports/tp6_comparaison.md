| Critere              | Manuel (TP 3)  | H2O AutoML        | FLAML          |
|----------------------|----------------|-------------------|----------------|
| F1 sur le jeu test   | 0.8669         | 0.8623            | 0.8359         |
| Modele retenu        | foret 300      | Stacked Ensemble  | LightGBM       |
| Latence mediane      | non servi      | 61 a 65 ms        | 10 a 12 ms     |
| Latence p95          | non servi      | 81 a 123 ms       | 14 a 17 ms     |
| Taille du modele     | 16.1 Mo (*)    | 5.1 Mo            | 43 Ko          |
| Dependances en prod  | Python         | Python + Java 17  | Python         |
|                      |                | + serveur H2O     | + lightgbm     |
| Survit a un          | oui            | non (modele perdu | oui            |
| redemarrage d'H2O    |                | -> erreur 400)    |                |
| Explicabilite        | bonne          | faible : meta-    | bonne :        |
|                      | (importances,  | modele sur 10     | un seul        |
|                      | un seul algo)  | modeles de base   | modele, SHAP   |

(*) models/model.pkl actuel = foret du pipeline DVC (600 arbres, profondeur 20),
    plus lourde que la foret 300 du TP 3 (7.8 Mo dans l'enonce).

Commentaire : H2O gagne quelques centiemes de F1 sur FLAML, mais coute environ
5 fois plus de latence, 120 fois plus de place et une JVM a maintenir en vie.
Pour un paiement en temps reel, FLAML (ou le modele manuel) est le meilleur compromis.
