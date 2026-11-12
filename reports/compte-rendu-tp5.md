# TP 5 — Explorer les plateformes AutoML et low-code : compte rendu

## Résultats mesurés

| Étape | Résultat |
|---|---|
| Référence (régression logistique) | F1 = 0.7407 |
| FLAML 10 s / 60 s / 120 s | F1 = 0.8514 / 0.8359 / 0.8636 (modèles retenus : lgbm / xgboost / lgbm ; 3 runs dans l'expérience MLflow `tp5-automl`) |
| Journal FLAML (`reports/flaml.log`) | 8 lignes : une ligne par meilleur essai + la ligne `curr_best_record_id` |
| Orange, avant amélioration | LogReg 0.781 · kNN 0.491 (CA 0.906, rappel 0.401) · Tree 0.756 · RF 10 arbres 0.813 · GB 0.837 |
| Orange, après amélioration | kNN normalisé 0.780 · RF 100 arbres 0.833 |
| Orange, matrice du GB | 113 fraudes détectées / 142, 29 manquées, 15 fausses alertes |
| KNIME (LogReg / RF / GBT) | LogReg 0.762 · RF 0.822 · GBT 0.844 (Scorer, ligne de la classe 1) |
| KNIME, matrice du GBT | 111 fraudes détectées / 142, 31 manquées, 10 fausses alertes (total 1 250, exactitude 0,967) |
| KNIME, composant AutoML | modèle retenu : **XGBoost Trees**, F-measure = 0.843 (test stratifié 20 %, 1 000 lignes ; CV 4 plis). Classement : XGBoost 0.843 · Neural Network 0.833 · GBT 0.817 · RF 0.804 · Decision Tree 0.780 · GLM (H2O) 0.757 · LogReg 0.623 · Naive Bayes 0.462. Workflow de déploiement écrit dans `models/knime-automl` |

### Réglage Orange corrigé

Le workflow `fraude-tp5.ows` avait été enregistré avec *Stratify sample* **décoché** dans Data Sampler (l'énoncé demande de le cocher). Sans stratification, les F1 étaient différents (LogReg 0.725, GB 0.804, RF 0.826, Tree 0.672). Après avoir coché la case, on retrouve les valeurs ci-dessus ; le workflow et `models/fraude-gb.pkcls` ont été réenregistrés dans cet état.

## Captures (`reports/captures/`)

| Fichier | Contenu |
|---|---|
| `orange-workflow.jpg` | workflow Orange complet de la partie A |
| `orange-test-and-score-avant.jpg` | Test and Score avant amélioration (kNN sans normalisation, RF 10 arbres) |
| `orange-test-and-score-apres.jpg` | Test and Score après amélioration (kNN normalisé, RF 100 arbres) |
| `orange-matrice-gb.jpg` | matrice de confusion du Gradient Boosting (1093 / 15 / 29 / 113) |
| `knime-workflow.jpg` | workflow KNIME complet (nœuds 1 à 14) |
| `knime-scorer-logreg-*.jpg`, `knime-scorer-rf-*.jpg`, `knime-scorer-gbt-*.jpg` | matrice de confusion et Accuracy statistics des trois Scorers |
| `knime-automl-vue.jpg` | vue du composant AutoML (classement par F-measure, XGBoost retenu) |

### Réglages KNIME à connaître (constatés pendant les étapes 8 et 9)

Avec KNIME 5.12, trois réglages « par défaut » donnaient des scores aberrants ; ils ont été corrigés avant de relever les F1 :

- **Logistic Regression Learner** : le solveur par défaut *Stochastic average gradient* ne converge pas sur des variables non normalisées (`montant` va jusqu'à 55 000) ; le modèle prédisait toujours « 0 » (F1 indéfini). Solveur passé à *Iteratively reweighted least squares* : F1 = 0.762.
- **Random Forest Learner** : la boîte de dialogue moderne enregistre `isUseDifferentAttributesAtEachNode = false`, c'est-à-dire 2 variables tirées **par arbre** (racine de 4) au lieu de **par nœud**. La moitié des arbres ne voyait jamais `montant` et le vote majoritaire écrasait les fraudes : F1 = 0.068. Le réglage n'étant pas exposé dans la boîte de dialogue, il a été passé à `true` dans `settings.xml` du nœud : F1 = 0.822.
- **Gradient Boosted Trees Learner** : même échantillonnage de colonnes par défaut (*Square root*, même jeu pour tout l'arbre) et profondeur non limitée : F1 = 0.463. Avec *All columns* et la profondeur 4 de l'énoncé : F1 = 0.844.

Leçon MLOps : un réglage par défaut n'est pas un réglage neutre ; il faut le lire dans le workflow (ici `settings.xml`, versionnable) et vérifier un score aberrant avant de comparer des outils.

## Questions

### 1. kNN : 0,904 d'exactitude mais 0,478 de F1 (mesuré chez nous : 0,906 et 0,491). Pourquoi ? Pourquoi la normalisation le fait passer à 0,780 ?

Les classes sont déséquilibrées : 11 % de fraudes seulement. Un modèle qui répond toujours « pas de fraude » atteint déjà 0,886 d'exactitude. L'exactitude est donc dominée par la classe 0 et ne dit presque rien de la détection des fraudes. Le F1 de la classe 1 combine précision et rappel sur les fraudes : avec un rappel de 0,401 (mesuré), le kNN rate six fraudes sur dix, d'où un F1 de 0,491 (0,478 dans l'énoncé).

Le kNN classe un point selon ses voisins les plus proches, mesurés par une distance euclidienne. Sans normalisation, la colonne `montant` (des centaines de dirhams) a une amplitude bien plus grande que `anciennete`, `freq_24h` ou `nuit` (0/1) : la distance ne dépend pratiquement que du montant. La standardisation (moyenne 0, variance 1) donne le même poids à chaque variable : les autres signaux de fraude (fréquence, nuit) comptent enfin, et le F1 monte à 0,780.

### 2. Pourquoi un F1 qui change d'une exécution à l'autre pose problème en MLOps ? Réglages équivalents ?

Le MLOps repose sur la reproductibilité : à code, données et paramètres identiques, on doit obtenir le même modèle. Sinon :
- on ne peut pas comparer deux versions (un gain de 0,015 peut venir du hasard et non de la modification) ;
- on ne peut pas reproduire un modèle en production pour l'auditer ou le corriger ;
- les tests de non-régression d'un pipeline CI deviennent instables.

Réglages équivalents (graine aléatoire fixe) :
- Orange : case *Replicable training* (Random Forest) et *Replicable (deterministic) sampling* (Data Sampler) ;
- KNIME : *Use static random seed* (Random Forest Learner) et *fixed random seed* (Table Partitioner) ;
- scikit-learn : paramètre `random_state=42` ;
- FLAML : paramètre `seed` de `AutoML.fit()`. Il manquait dans notre `src/automl.py`, ce qui explique en partie le F1 du budget 60 s plus faible que celui de 10 s.

### 3. 29 fraudes manquées, 15 fausses alertes : laquelle coûte le plus cher ? Quel réglage déplace l'équilibre ?

La fraude manquée (faux négatif) coûte le plus cher : la banque perd le montant de la transaction, rembourse le client et perd sa confiance. Une fausse alerte (faux positif) coûte seulement une vérification (appel, SMS, blocage temporaire de la carte).

Pour détecter plus de fraudes, quitte à avoir plus de fausses alertes :
- **baisser le seuil de décision** (par défaut 0,5) sur la probabilité de fraude : on augmente le rappel au prix de la précision. Dans Orange, le widget ROC Analysis et la colonne de probabilité de Predictions permettent de choisir ce seuil ;
- **pondérer les classes** (`class_weight='balanced'` dans scikit-learn) ou rééchantillonner (sur-échantillonner les fraudes) ;
- optimiser une métrique qui favorise le rappel (F2 au lieu de F1).

### 4. Pourquoi KNIME exige-t-il Number to String ? Équivalent dans Orange ? Et si on l'oublie ?

Dans KNIME, les Learners de classification exigent une cible nominale (des catégories). La colonne `fraude` est lue comme un entier, donc comme une quantité : elle n'apparaît pas dans la liste *Target column*, et le nœud reste au rouge. Number to String la transforme en texte « 0 » / « 1 », donc en catégorie.

Dans Orange, le geste équivalent se fait dans le widget File : passer le *Role* de `fraude` à *target* et son *Type* à *categorical*. Si on l'oublie, Orange traite le problème comme une **régression** : Test and Score affiche MSE et RMSE au lieu de F1, et le modèle prédit une valeur continue au lieu d'une classe.

### 5. Composant AutoML de KNIME vs FLAML : automatisé, à votre charge, trace laissée

| | FLAML | Composant AutoML de KNIME |
|---|---|---|
| Automatisé | choix de la famille de modèles (lgbm, rf, xgboost, extra_tree...) et des hyperparamètres dans un budget de temps | préparation des données, entraînement de plusieurs familles, réglage par validation croisée, choix du meilleur, création du workflow de déploiement |
| À votre charge | lire et préparer les données, choisir la métrique, le budget, la graine, le partage de test ; écrire le code de journalisation et de service | choisir la cible, la classe positive, la métrique, cocher les modèles ; installer les extensions ; servir le modèle (Business Hub, payant) |
| Trace | `reports/flaml.log` (une ligne par essai : configuration, temps, perte), `best_config`, et les runs MLflow | vue du composant (classement des modèles et scores) et workflow de déploiement ; le détail des essais reste dans le composant, plus difficile à auditer et à versionner |

FLAML est plus transparent et s'intègre directement au pipeline MLOps (Python, MLflow, Git) ; le composant KNIME va plus loin dans l'automatisation (préparation et déploiement) mais laisse une trace moins exploitable.

### 6. Versionner `fraude-tp5.ows`, `tp5-fraude.knwf` et `fraude-gb.pkcls` ? Que manque-t-il pour servir le modèle ?

- `workflows/fraude-tp5.ows` : c'est un fichier XML texte qui décrit widgets, liens et réglages. Il se versionne dans **Git** comme du code (TP 4 bis), avec des différences lisibles.
- `tp5-fraude.knwf` : c'est une archive zip (binaire), donc des différences illisibles dans Git. On peut la suivre avec **DVC** (ou Git LFS), ou versionner le dossier du workflow exporté sans les données.
- `models/fraude-gb.pkcls` : artefact binaire de ~320 Ko produit par l'entraînement. Il se suit avec **DVC** (TP 4), le `.dvc` allant dans Git, ou s'enregistre comme artefact d'un run MLflow avec ses métriques.

Appliqué dans ce dépôt : `fraude-tp5.ows` est suivi par Git ; `tp5-fraude.knwf` et `fraude-gb.pkcls` sont suivis par DVC (`workflows/tp5-fraude.knwf.dvc`, `models/fraude-gb.pkcls.dvc`, envoyés sur le remote `local`), seuls les `.dvc` vont dans Git.

Ce qui manque pour la production :
- **Orange** s'arrête au fichier `.pkcls` : il n'y a ni API REST, ni planification, ni registre de modèles, ni suivi. Servir le modèle demande du code Python (charger le pickle dans une API FastAPI par exemple), et le pickle dépend de la version exacte d'Orange.
- **KNIME Analytics Platform** exécute les workflows sur le poste seulement. L'exposition en service REST, la planification, la gestion des versions et la surveillance relèvent de **KNIME Business Hub**, l'offre serveur payante.

### 7. Le manuel (0,8669) et FLAML (0,8636) battent Orange et KNIME. Cela remet-il en cause le low-code ?

Non. L'écart (2 à 3 centièmes de F1) est faible, et en partie dû aux protocoles différents (partage stratifié ou non, réglages par défaut dans Orange et KNIME). Le low-code ne vise pas le meilleur score, mais :
- la **rapidité** du prototypage et de l'exploration visuelle (matrice de confusion, ROC, prédictions) ;
- l'**accessibilité** pour des profils qui ne codent pas ;
- la **communication** : un workflow visuel s'explique facilement à des métiers ou à un auditeur.

Je le recommande pour : les analystes métier et les débutants, l'enseignement, les preuves de concept et l'exploration d'un nouveau jeu de données. Pour un modèle critique en production (comme la détection de fraude), un pipeline en code (manuel ou FLAML) reste préférable : meilleur score, reproductibilité, versionnement Git/DVC et intégration MLflow plus simples.
