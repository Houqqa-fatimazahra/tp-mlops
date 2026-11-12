# TP 9 — Conteneuriser un modèle avec Docker et le déployer sur Kubernetes

**Compte rendu** · Fatima Zahra Houqqa · Partie 7 du cours (MLOps)

## Sommaire

1. [Environnement et déroulement](#1-environnement-et-déroulement)
2. [Livrable 1 — Le dossier fraude-api commité dans Git](#2-livrable-1--le-dossier-fraude-api-commité-dans-git)
3. [Livrable 2 — 0,8899 dans Docker et dans Kubernetes](#3-livrable-2--08899-dans-docker-et-dans-kubernetes)
4. [Livrable 3 — Les deux durées de reconstruction (étape 9)](#4-livrable-3--les-deux-durées-de-reconstruction-étape-9)
5. [Livrable 4 — kubectl get pods avant et après la suppression d'un pod](#5-livrable-4--kubectl-get-pods-avant-et-après-la-suppression-dun-pod)
6. [Livrable 5 — Le client pendant la mise à jour et pendant la version en panne](#6-livrable-5--le-client-pendant-la-mise-à-jour-et-pendant-la-version-en-panne)
7. [Réponses aux questions](#7-réponses-aux-questions)
8. [Tableau avantage / mesure obtenue](#8-tableau-avantage--mesure-obtenue)
9. [Écarts avec l'énoncé](#9-écarts-avec-lénoncé)

---

## 1. Environnement et déroulement

| Élément | Version |
|---|---|
| Système | Windows 11 Home, PowerShell 5.1 |
| Docker Desktop (moteur) | 29.1.2 (WSL 2, 8 Go de mémoire, 16 processeurs) |
| kubectl (client) | v1.34.1 (fourni par Docker Desktop) |
| kind | v0.33.0 windows/amd64 (installé par `winget install -e --id Kubernetes.kind`) |
| Kubernetes du cluster | v1.37.0 (image `kindest/node:v1.37.0`) |
| Python machine / image | 3.13.9 (`.venv`) / 3.12.16 (`python:3.12-slim`) |
| Bibliothèques de l'image | fastapi 0.162.0, uvicorn 0.54.0, scikit-learn 1.9.1, pandas 3.1.0, joblib 1.6.0 |

Le dossier suivi dans tout le TP est celui de **Mme Benali** : `{"montant": 1800, "anciennete": 30, "freq_24h": 4, "nuit": 1}`.

Toutes les sorties brutes sont dans `reports/tp9_sorties.txt` ; les captures sont dans `reports/captures/tp9-*.png`.

| Étape | Résultat obtenu | Point de contrôle du cours |
|---|---|---|
| 1. Premiers conteneurs | machine Python 3.13.9, conteneur **Python 3.12.16** ; `essai` visible en `Exited (0)` dans `docker ps -a`, puis supprimé | identique |
| 2. Projet | `sklearn.__version__` = **1.9.1** ; `models/model.pkl` copié (même empreinte SHA-256 que l'original) | identique |
| 3 à 5. Fichiers | `api/main.py`, `api/client.py`, `requirements.txt`, `Dockerfile`, `.dockerignore` | identique |
| 6. Construction | `pip install` 188,6 s ; image `fraude-api:1.0`, ID **49d55fd465f4**, 695 Mo sur disque / 158 Mo de contenu | 918 Mo / 229 Mo (variable) |
| 7. Test | `/health` → `ok 1.0 81f8906cf5cf` ; `/predict` → **True 0.8899** ; requête sans `nuit` → **422** | identique |
| 8. Observation | sklearn **1.9.1** dans le conteneur ; 141,5 Mio, 0,26 % CPU ; arrêt puis suppression | identique |
| 9. Cache | bon ordre **2,8 s** ; mauvais ordre **187,4 s** après modification (230,2 s la 1re fois) | 0,6 s / 50,3 s |
| 10. Portabilité | `fraude-api-1.0.tar` = 150,9 Mo ; même ID **49d55fd465f4** après `docker load` | identique |
| 11. Cluster | nœud `tp-mlops-control-plane` **Ready** ; image chargée par `kind load` | identique |
| 13. Déploiement | 2 pods `0/1 Running` puis `1/1` en 12 s ; « Readiness probe failed » ×2 au démarrage | identique |
| 14. Appel | `{"fraude":true,"probabilite":0.8899,"version":"1.0","hote":"fraude-api-7b597b698c-knjt4"}` | identique |
| 15. Répartition | 2 pods, 0 erreur ; 52 / 42 réponses | identique |
| 16. 4 pods | 4 pods, 0 erreur ; 19 / 18 / 14 / 12 réponses | identique |
| 17. Auto-réparation | pod `knjt4` supprimé → pod `8vhxd` recréé (AGE 3 s), prêt en 14 s | identique |
| 18. Mise à jour 2.0 | **394 requêtes, 0 erreur** ; v1.0 et v2.0 ensemble pendant ~14 s | 538 requêtes, 0 erreur |
| 19. Version en panne | 2.1 en échec (`FileNotFoundError: models/modele.pkl`), **513 requêtes, 0 erreur** ; `rollout undo` → révisions 1, 3, 4 | 673 requêtes, 0 erreur |
| Q7 (facultatif) | même mise à jour **sans `preStop`** : **11 erreurs sur 404 requêtes** | 7 erreurs sur 533 |
| 20. Nettoyage | Deployment, Service et cluster supprimés ; images 2.0 et 2.1 et fichier .tar supprimés ; `fraude-api:1.0` conservée | identique |

---

## 2. Livrable 1 — Le dossier fraude-api commité dans Git

```
fraude-api/
├── api/
│   ├── main.py          service FastAPI : /health et /predict (+ champ hote)
│   └── client.py        client de test lancé dans un pod (partie B)
├── models/
│   └── model.pkl        forêt du TP 3 (suivie par DVC, voir § 9)
├── k8s/
│   ├── deployment.yaml  2 pods, readinessProbe, preStop sleep 5, requests/limits
│   └── service.yaml     adresse unique http://fraude-api (port 80 → 8000)
├── requirements.txt     5 bibliothèques figées avec ==
├── Dockerfile           bibliothèques d'abord, code et modèle ensuite
└── .dockerignore        .venv, data, __pycache__, .git, *.tar
```

`api/main.py` est revenu à son état d'origine après les étapes 9, 18 et 19 (`VERSION = "1.0"`, `models/model.pkl`, sans les lignes `# modification`). Le fichier `Dockerfile.mauvais` et le fichier `.tar` ont été supprimés.

---

## 3. Livrable 2 — 0,8899 dans Docker et dans Kubernetes

**Docker (étape 7)** — `reports/captures/tp9-docker-0.8899.png`

```
statut version hote
------ ------- ----
ok     1.0     81f8906cf5cf

fraude probabilite version hote
------ ----------- ------- ----
  True      0.8899 1.0     81f8906cf5cf

code HTTP requete incomplete : 422
```

La page `http://localhost:8000/docs` (Swagger généré par FastAPI) est capturée dans `reports/captures/tp9-docker-docs.png` : `GET /health`, `POST /predict` et le schéma `Transaction`.

**Kubernetes (étape 14)** — `reports/captures/tp9-k8s-0.8899.png`

```
{"statut":"ok","version":"1.0","hote":"fraude-api-7b597b698c-knjt4"}
{"fraude":true,"probabilite":0.8899,"version":"1.0","hote":"fraude-api-7b597b698c-knjt4"}
```

Le champ `hote` contient l'identifiant du conteneur dans Docker (`81f8906cf5cf`), puis le nom d'un pod dans Kubernetes.

---

## 4. Livrable 3 — Les deux durées de reconstruction (étape 9)

`reports/captures/tp9-cache-durees.png`

| Reconstruction après modification de `api/main.py` | Étape `pip install` | Durée totale |
|---|---|---|
| Dockerfile du cours (bon ordre), image `fraude-api:1.1` | **CACHED** | **2,8 s** |
| `Dockerfile.mauvais` (`COPY . .` avant `pip install`) | refaite : 157,1 s | **187,4 s** |
| *(pour mémoire : mauvais ordre, première construction)* | 201,5 s | 230,2 s |

Rapport : environ **67 fois plus lent** avec le mauvais ordre. Les durées sont plus longues que dans l'énoncé parce que la connexion était lente (pip télécharge environ 150 Mo à chaque fois), mais l'écart est le même.

---

## 5. Livrable 4 — kubectl get pods avant et après la suppression d'un pod

`reports/captures/tp9-k8s-pods-avant.png` et `reports/captures/tp9-k8s-pods-apres.png`

```
AVANT
fraude-api-7b597b698c-knjt4   1/1     Running   0          57s
fraude-api-7b597b698c-p7lsj   1/1     Running   0          57s
fraude-api-7b597b698c-p82ps   1/1     Running   0          23s
fraude-api-7b597b698c-zmjhf   1/1     Running   0          23s

kubectl delete pod fraude-api-7b597b698c-knjt4

JUSTE APRES (3 s)
fraude-api-7b597b698c-8vhxd   0/1     Running       0          3s     <- recree par Kubernetes
fraude-api-7b597b698c-knjt4   1/1     Terminating   0          60s
...
QUELQUES SECONDES PLUS TARD
fraude-api-7b597b698c-8vhxd   1/1     Running   0          14s
fraude-api-7b597b698c-p7lsj   1/1     Running   0          71s
fraude-api-7b597b698c-p82ps   1/1     Running   0          37s
fraude-api-7b597b698c-zmjhf   1/1     Running   0          37s
```

Le pod `8vhxd` (AGE 3 s) a été créé par le Deployment, sans aucune commande de notre part : l'état réel (3 pods) a été ramené à l'état souhaité (4 pods).

---

## 6. Livrable 5 — Le client pendant la mise à jour et pendant la version en panne

**Étape 18 — mise à jour 1.0 → 2.0** — `reports/captures/tp9-rolling-update-client.png`

```
17:47:01 {'v1.0': 18} pods: 2 erreurs: 0
17:47:03 {'v1.0': 14, 'v2.0': 4} pods: 3 erreurs: 0
17:47:05 {'v1.0': 9, 'v2.0': 12} pods: 2 erreurs: 0
...
17:47:15 {'v1.0': 2, 'v2.0': 18} pods: 3 erreurs: 0
17:47:18 {'v2.0': 20} pods: 2 erreurs: 0
reponses par pod : {'...-p7lsj': 87, '...-zmjhf': 148, '...-9jf9q': 110, '...-cchtr': 49}
```

Total : 87 + 148 + 110 + 49 = **394 requêtes, 0 erreur**. Les deux versions ont répondu ensemble de 17:47:03 à 17:47:15 (environ 14 s). `rollout history` affiche les révisions 1 et 2.

**Étape 19 — version 2.1 en panne, puis retour arrière** — `reports/captures/tp9-version-panne-client.png` et `tp9-version-panne-rollback.png`

```
error: timed out waiting for the condition
fraude-api-5646748c6d-9jf9q   1/1     Running   0             103s
fraude-api-5646748c6d-cchtr   1/1     Running   0             92s
fraude-api-5d84bf5589-zdccw   0/1     Error     2 (32s ago)   40s
FileNotFoundError: [Errno 2] No such file or directory: 'models/modele.pkl'
deployment.apps/fraude-api rolled back
deployment "fraude-api" successfully rolled out
REVISION  1  3  4
```

Côté client : uniquement `{'v2.0': ...}` et `erreurs: 0` du début à la fin, soit 245 + 268 = **513 requêtes, 0 erreur**. Le pod 2.1 alterne entre `Error` et `CrashLoopBackOff` (2 redémarrages en 40 s) ; il n'est jamais prêt, il ne reçoit donc aucune requête. `rollout undo` crée la révision 4, qui est l'ancienne révision 2 (version 2.0).

---

## 7. Réponses aux questions

**1. Image et conteneur.** Une **image** est un modèle figé, en lecture seule : `python:3.12-slim` contient un système minimal et Python 3.12. Un **conteneur** est une exécution de cette image, avec son propre état. À l'étape 1, la même image a donné trois conteneurs différents. Le conteneur `essai`, lancé sans `--rm`, est resté visible en `Exited (0)` dans `docker ps -a` jusqu'au `docker rm`. Supprimer le conteneur ne supprime pas l'image (`docker images`). Le code est copié dans l'image au moment du `docker build` : après une modification de `api/main.py`, il faut donc **reconstruire l'image** (`docker build -t fraude-api:1.1 .`), arrêter et supprimer l'ancien conteneur, puis en **lancer un nouveau** à partir de la nouvelle image. Dans Kubernetes, il faut en plus charger l'image (`kind load`) puis faire `kubectl set image`, comme à l'étape 18.

**2. Pourquoi `==`.** Le signe `==` fige la version exacte : l'image construite aujourd'hui ou dans six mois contiendra les mêmes bibliothèques, donc le même comportement. Sans version, `pip` installerait la dernière version de scikit-learn disponible le jour de la construction. Un modèle sauvegardé avec `pickle`/`joblib` dépend des classes internes de la version qui l'a créé. On risquerait alors un avertissement `InconsistentVersionWarning`, une erreur au chargement (attribut manquant), ou pire, des **probabilités légèrement différentes sans aucun message**. Nous l'avons d'ailleurs observé (§ 9) : les logs du conteneur indiquent que `model.pkl` a été sauvegardé avec scikit-learn **1.8.0**. Le résultat reste 0,8899 entre 1.8.0 et 1.9.1, mais rien ne le garantit pour une version future.

**3. Durées de reconstruction.** **2,8 s** avec le bon ordre, contre **187,4 s** avec le mauvais (§ 4). Chaque instruction du Dockerfile produit une **couche**. Docker réutilise une couche du **cache** tant que l'instruction et ses fichiers d'entrée n'ont pas changé ; dès qu'une couche change, toutes les suivantes sont refaites. Avec le bon ordre, `COPY requirements.txt` et `RUN pip install` ne dépendent pas de `api/main.py` : ils restent `CACHED`, et seules les couches `COPY api/` et `COPY models/` sont refaites. Avec `COPY . .` en premier, la moindre modification du code invalide cette couche, donc aussi le `RUN pip install` qui la suit : pip retélécharge et réinstalle tout (157 s).

**4. RUN, CMD, 0.0.0.0, EXPOSE.** `RUN` s'exécute **pendant la construction**, et son résultat est enregistré dans une couche de l'image (ici, les bibliothèques installées). `CMD` est la commande lancée **au démarrage de chaque conteneur** ; il n'y en a qu'une, et `docker run ... commande` peut la remplacer (c'est ce que fait le client avec `python api/client.py`). `--host 0.0.0.0` fait écouter uvicorn sur toutes les interfaces du conteneur. Avec la valeur par défaut, `127.0.0.1`, il n'accepterait que les connexions venant du conteneur lui-même : la redirection de port de Docker, ou un autre pod, recevrait « connection refused ». `EXPOSE 8000` **ne suffit pas** : c'est seulement de la documentation dans l'image. C'est `-p 8000:8000` qui publie réellement le port sur la machine. Dans Kubernetes, c'est le Service, ou `kubectl port-forward`, qui rend le pod joignable.

**5. Deployment, Service, étiquette.** Le **Deployment** décrit l'état souhaité (2 pods à partir de `fraude-api:1.0`, avec la sonde et les ressources). Il crée les pods, les recrée s'ils disparaissent (étape 17) et les remplace progressivement lors d'une mise à jour (étape 18). Le **Service** donne aux pods une adresse stable, `http://fraude-api` (ClusterIP `10.96.21.240`, port 80 → 8000), et répartit les requêtes entre les pods prêts. L'**étiquette `app: fraude-api`** fait le lien : le `selector` du Deployment désigne les pods qu'il gère, et le `selector` du Service désigne ceux qui reçoivent le trafic. Avec `app: fraude` dans le Service, **aucun pod ne correspondrait**. Le Service existerait mais n'aurait aucun point d'accès (endpoints vides) : le client recevrait une erreur pour chaque requête (connexion refusée ou délai dépassé), alors que les pods tourneraient normalement.

**6. 0/1 puis 1/1, et readinessProbe.** `0/1 Running` signifie que le conteneur tourne, mais que la `readinessProbe` (`GET /health`) n'a pas encore réussi. uvicorn met environ 1 à 2 s à démarrer et à charger le modèle : d'où les deux « Readiness probe failed: connection refused » de l'étape 13. Le pod passe à `1/1` une fois `/health` en 200. **Sans `readinessProbe`**, Kubernetes considère un pod prêt dès que son conteneur démarre. Lors du passage à la 2.1, le pod en panne aurait été ajouté au Service à chaque redémarrage, et une partie des requêtes du client serait tombée dessus (erreurs). Surtout, le Deployment l'aurait cru disponible : il aurait continué la mise à jour et **arrêté les pods 2.0**. On se serait retrouvé avec 2 pods 2.1 en `CrashLoopBackOff` et un service totalement indisponible. Avec la sonde, la mise à jour s'est bloquée sur le premier pod et le client a gardé 0 erreur.

**7. Erreurs pendant la mise à jour et preStop.** **0 erreur sur 394 requêtes** à l'étape 18. Quand Kubernetes arrête un pod, deux actions partent en parallèle : il retire le pod des points d'accès du Service, et il envoie SIGTERM au conteneur. Sans délai, le conteneur peut s'arrêter avant que tous les composants du cluster aient cessé de lui envoyer du trafic : quelques requêtes arrivent alors sur un pod fermé. `preStop: sleep 5` retarde le SIGTERM de 5 s, ce qui laisse le temps au retrait du Service de se propager et aux requêtes en cours de se terminer. **Expérience facultative réalisée** : après avoir retiré `lifecycle.preStop` (`kubectl patch`), la même mise à jour (2.0 → 1.0) a donné **11 erreurs sur 404 requêtes**, à chaque arrêt d'un ancien pod (17:49:38 : 1 ; 17:49:48 : 7 ; 17:49:50 : 3). Capture : `reports/captures/tp9-sans-prestop-client.png`.

**8.** Voir le tableau ci-dessous.

---

## 8. Tableau avantage / mesure obtenue

| Avantage | Mesure obtenue |
|---|---|
| **Cohérence** | Même probabilité pour Mme Benali dans les trois environnements : **0,8899** sur la machine (TP 8), **0,8899** dans Docker (étape 7), **0,8899** dans Kubernetes (étape 14). Même version de scikit-learn, **1.9.1**, dans l'image (`docker exec`). |
| **Portabilité** | L'image tient dans un fichier de **150,9 Mo** (`docker save`). Après `docker rmi` puis `docker load`, l'identifiant est identique : **49d55fd465f4**. `kind load` utilise le même mécanisme pour transmettre l'image au cluster, qui l'a exécutée sans téléchargement (`already present on machine`). Le conteneur relance le service en ~2 s. |
| **Évolutivité** | 2 pods : 94 réponses en 10 s, réparties 52 / 42, 0 erreur (étape 15). Montée à **4 pods** en une commande, prêts en ~12 s, réparties 19 / 18 / 14 / 12, 0 erreur (étape 16). **Auto-réparation** : pod supprimé remplacé en 3 s, prêt en 14 s (étape 17). Mise à jour : **0 erreur / 394** ; version en panne : **0 erreur / 513** puis retour arrière en une commande (étapes 18 et 19). |

---

## 9. Écarts avec l'énoncé

- **Docker Desktop ne démarrait pas** (« Docker Desktop encountered an unexpected error ») : des fichiers de socket d'une session précédente (`%LOCALAPPDATA%\Docker\run\dockerInference`, puis `%LOCALAPPDATA%\docker-secrets-engine\engine.sock`) ne pouvaient plus être supprimés. Corrigé en fermant Docker Desktop (Quit, **sans** « Reset to factory defaults »), puis en renommant ces deux dossiers en `*.old-*`. Docker les a recréés proprement au redémarrage.
- **Version du modèle** : les logs du conteneur affichent `InconsistentVersionWarning: Trying to unpickle estimator RandomForestClassifier from version 1.8.0 when using version 1.9.1`. Le `model.pkl` du TP 3 a donc été sauvegardé avec scikit-learn 1.8.0, et `.venv` a été mis à jour ensuite. La prédiction reste exactement **0,8899** ; l'énoncé suppose 1.9.1 à l'entraînement. Pour supprimer l'avertissement, il faudrait réentraîner le modèle en 1.9.1 (non fait, pour ne pas changer le modèle de référence des TP précédents).
- **Durées** de l'étape 9 plus longues que dans l'énoncé (connexion lente pour pip), avec le même rapport.
- **Taille de l'image** : 695 Mo / 158 Mo, contre 918 Mo / 229 Mo dans l'énoncé (variable selon la version de l'image de base).
- **Versions** : kubectl client v1.34.1 (celui de Docker Desktop) avec un cluster v1.37.0 ; aucun problème rencontré.
- `.dockerignore` contient en plus `*.tar`, pour que le fichier de 150 Mo de l'étape 10 ne soit pas envoyé au moteur lors des constructions 2.0 et 2.1.
- Étape 19 : au moment du `kubectl get pods`, le pod 2.1 était affiché `Error` (entre deux redémarrages) plutôt que `CrashLoopBackOff` ; c'est le même cycle (2 redémarrages en 40 s).
- Le client du port-forward (étape 14) a été lancé dans le même script, en arrière-plan, au lieu d'un second terminal ; les captures « terminal » ont été produites à partir des sorties réelles de `reports/tp9_sorties.txt`.
- `fraude-api/models/model.pkl` est suivi par **DVC**, comme `models/model.pkl` (même contenu, même empreinte), et non directement par Git.
