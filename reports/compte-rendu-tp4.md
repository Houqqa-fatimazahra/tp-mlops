# Compte rendu TP 4 — Versionner données et expérimentations avec DVC

**Module :** Déploiement d'applications intelligentes · MLOps
**Étudiante :** Houqqa Fatima Zahra
**Date :** 18 octobre 2026
**Environnement :** Windows, PowerShell, dépôt `tp-mlops`, branche `master`, stockage distant local `C:\dvcstore`

## 1. Synthèse du travail réalisé

| Étape | Réalisation | Preuve |
|---|---|---|
| Installation | DVC initialisé, remote `local` (`C:\dvcstore`) par défaut | `.dvc/config`, dossier `C:\dvcstore\files` |
| 2 et 3 | Jeu de données versionné en v1 puis v2 (montants × 1,3) | tags `v1`, `v2`, `data/transactions.csv.dvc` |
| 4 | Retour arrière complet code + données | `git checkout v1; dvc checkout` |
| 5 | Pipeline décrit dans `dvc.yaml` | `dvc.yaml`, `dvc.lock` |
| 6 | Cache et déclenchement ciblé | `didn't change, skipping`, `is cached` |
| 7 | Trois expérimentations comparées | `03_dvc_exp_show.txt` |
| 8 | Clone d'un collègue et `dvc pull` | MD5 identiques (`04_preuve_clone_dvc_pull_md5.txt`) |

Synchronisation avec le stockage distant : `dvc status -c` → `Cache and remote 'local' are in sync.`
Historique Git et tags : voir `05_git_et_remote.txt`.

## 2. Cache et déclenchement ciblé

Premier `dvc repro` (exécution complète) : voir `01_dvc_repro_execution.txt`. Les trois étapes `preparer`, `entrainer`, `evaluer` s'exécutent (f1 = 0,8593).

Second `dvc repro` : les trois étapes sont ignorées (`didn't change, skipping`) et DVC affiche `Data and pipelines are up to date.` (voir `02_dvc_repro_cache.txt`).

Lors d'un changement de `max_depth` seul, `preparer` est ignorée et seules `entrainer` et `evaluer` sont rejouées. La troisième expérimentation (`n_estimators=600`, `max_depth=20`) reprend les paramètres déjà présents dans `master` : DVC retrouve les sorties dans le cache au lieu de réentraîner.

## 3. Comparaison des expérimentations

| Expérimentation | Paramètres | f1 | precision | recall |
|---|---|---|---|---|
| `master` (référence) | `max_depth=20`, `n_estimators=600` | 0,8593 | 0,876 | 0,8433 |
| `kinky-rotl` | `max_depth=8` | 0,8594 | **0,9016** | 0,8209 |
| `focal-dolt` | `max_depth=16` | **0,8659** | 0,8898 | 0,8433 |
| `undug-loge` | `n_estimators=600`, `max_depth=20` | 0,8593 | 0,876 | 0,8433 |

- `focal-dolt` (`max_depth=16`) obtient le meilleur f1 (0,8659), soit environ +0,007 par rapport à la référence.
- `kinky-rotl` (`max_depth=8`) a la meilleure précision (0,9016) mais un rappel plus faible (0,8209) : un arbre moins profond est plus prudent et détecte moins de fraudes.
- `undug-loge` reprend les paramètres de `master` et donne des métriques identiques, ce qui confirme la reproductibilité.
- Les écarts de f1 sont faibles et mesurés sur un seul découpage train/test : ils ne suffisent pas à conclure avec certitude.
- Aucun commit Git n'a été créé pour ces essais.

## 4. Preuve du clone et de `dvc pull`

Le dépôt a été cloné dans `$env:TEMP\collegue`. Le CSV n'y figurait pas (seul `transactions.csv.dvc`), puis `dvc pull` l'a téléchargé.

    MD5   21E203794A21E494F757CE4D886C6265   (dépôt d'origine)
    MD5   21E203794A21E494F757CE4D886C6265   (clone après dvc pull)

Les empreintes sont identiques.

## 5. Réponses aux questions

### Question 1 — Pourquoi la taille de `.git` ne redescend-elle pas après suppression du gros fichier ?

Git stocke chaque version d'un fichier sous forme d'objet immuable dans `.git/objects`, rattaché au commit qui l'a créé. `git reset --hard HEAD~1` déplace seulement la branche vers le commit précédent et supprime le fichier du répertoire de travail. Le commit annulé et son contenu restent dans la base d'objets (accessibles par le reflog) tant qu'ils ne sont pas purgés explicitement (`git reflog expire`, `git gc --prune`, ou `git filter-repo` pour réécrire l'historique).

Le fichier a donc disparu du répertoire de travail mais pas de l'historique. Si le commit avait été poussé, chaque collègue qui clone le dépôt téléchargerait ce fichier de façon permanente. Git n'est pas conçu pour les gros fichiers binaires ou les données qui changent souvent : chaque modification ajoute une nouvelle copie complète.

### Question 2 — Que contient le fichier `.dvc`, et où se trouvent réellement les données ?

Le fichier `transactions.csv.dvc` est un petit pointeur texte versionné par Git :

    outs:
    - md5: 21e203794a21e494f757ce4d886c6265
      size: 86374
      hash: md5
      path: transactions.csv

Il contient l'empreinte MD5, la taille, l'algorithme de hachage et le chemin du fichier. Le contenu réel se trouve hors de Git : dans le cache local `.dvc/cache` (adressage par contenu) et, après `dvc push`, dans le stockage distant `C:\dvcstore\files\md5`. Le fichier `data/.gitignore` empêche Git de suivre le CSV lui-même : Git versionne le pointeur, DVC gère le contenu.

### Question 3 — Un collègue lance `git checkout v1` mais oublie `dvc checkout`. Que risque-t-il ?

`git checkout v1` ne ramène que le code et le pointeur `.dvc` de la version 1. Le fichier `data/transactions.csv` reste dans son état précédent (version 2) : l'état est incohérent, le code et le pointeur disent « v1 » alors que les données sont celles de la v2.

Le risque principal est que rien ne plante : il peut entraîner et évaluer un modèle en croyant travailler sur la v1 et obtenir des métriques faussées, non reproductibles et impossibles à comparer. `dvc status` signalerait la divergence (`modified: data/transactions.csv`). D'où la règle : `git checkout` et `dvc checkout` vont toujours par paire.

### Question 4 — Vous modifiez uniquement `max_depth`. Pourquoi la préparation n'est-elle pas rejouée ?

Chaque étape de `dvc.yaml` déclare ses dépendances (`deps`), ses paramètres (`params`) et ses sorties. DVC enregistre dans `dvc.lock` l'empreinte de chacun et ne rejoue une étape que si l'une d'elles a changé.

- `preparer` dépend de `src/preparer.py`, de `data/transactions.csv` et de `preparation.test_size`. `max_depth` n'en fait pas partie (il appartient à `entrainement`) : l'étape est ignorée.
- `entrainer` déclare `entrainement.max_depth` : son paramètre a changé, elle est rejouée.
- `evaluer` dépend de `models/model.pkl`, qui vient d'être régénéré : elle est rejouée à son tour.

DVC ne recalcule ainsi que la partie impactée du graphe.

### Question 5 — DVC et MLflow se recouvrent-ils ? Pourquoi utiliser les deux ?

Ils se recouvrent partiellement : tous deux enregistrent des paramètres et des métriques et comparent des essais. Leurs rôles principaux diffèrent.

| | DVC | MLflow |
|---|---|---|
| Rôle principal | Versionner données et artefacts, rendre le pipeline reproductible | Tracer les exécutions et gérer les modèles |
| Apporte | Pointeurs `.dvc`, cache et remote, `dvc.yaml`/`dvc.lock`, rejeu ciblé, retour arrière code + données, `dvc exp` | Journal des runs (paramètres, métriques, artefacts), interface de comparaison, registre de modèles, packaging (`MLproject`) |
| Intégration | S'appuie sur Git | Base de suivi (`mlflow.db`) et dossier d'artefacts (`mlartifacts`) |

On utilise les deux car ils sont complémentaires : DVC garantit que l'on sait avec quelles données et quel pipeline un résultat a été produit et que l'on peut le reproduire ; MLflow offre un historique détaillé et visuel des essais et un registre pour promouvoir et déployer les modèles.

## 6. Conclusion

Git seul ne convient pas aux données volumineuses : DVC versionne un pointeur léger dans Git et le contenu dans un stockage séparé. Le couple `git checkout` + `dvc checkout` restaure un état complet et cohérent. Le pipeline `dvc.yaml` ne rejoue que les étapes impactées, et `dvc exp` permet de comparer des réglages (`max_depth` de 8 à 20) sans polluer l'historique. Le meilleur compromis observé est `max_depth=16` (f1 = 0,8659).
