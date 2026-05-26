Architecture du Système
=======================

La conception technique de **KineAssist** privilégie la modularité, la performance en temps réel et la protection de la vie privée. L'intégralité du traitement de l'image par l'IA et de la recherche vectorielle RAG est exécutée sur la machine hôte.

----

1. Schéma du Pipeline de Traitement
-----------------------------------

Le traitement d'une session d'exercice suit un cycle itératif en temps réel :

.. code-block:: text

   +--------------------------------------------------------------+
   |                        FLUX VIDEO                            |
   |              Capture webcam via OpenCV (hote)                |
   +--------------------------------------------------------------+
                                  |
                                  v
   +--------------------------------------------------------------+
   |                     ESTIMATION DE POSTURE                    |
   |           MediaPipe Pose (33 points clés 3D)                 |
   +--------------------------------------------------------------+
                                  |
                                  v
   +--------------------------------------------------------------+
   |                     CALCUL DES ANGLES                        |
   |  Trigonométrie 2D sur les points clés (angle_calculator.py)  |
   +--------------------------------------------------------------+
                                  |
            +---------------------+---------------------+
            |                                           |
            v                                           v
   +--------------------+                      +--------------------+
   |  DETECTION REPS    |                      | RENDU VIDEO STREAM |
   | Automate à seuils  |                      | Tracé repères joint|
   +--------------------+                      | OpenCV + Streamlit |
            |                                  +--------------------+
            v
   +--------------------+
   |   SCORING DTW      |
   |  Comparaison avec  |
   |  courbe numpy ref  |
   +--------------------+
            |
            v
   +--------------------+
   |   MOTEUR RAG       |
   |  Recherche FAISS   |
   |  -> Correction vocal|
   +--------------------+

----

2. Structure des Fichiers du Projet
-----------------------------------

Le code source de KineAssist est organisé comme suit :

.. code-block:: text

   Kineassist/
   ├── app.py                     # Application Streamlit principale (Espace Patient)
   ├── auth.py                    # Formulaires d'authentification (Kiné / Patient)
   ├── database.py                # Initialisation et requêtes SQLite (Bcrypt)
   ├── run.py                     # Script de démarrage combiné (Streamlit + Landing Page)
   ├── sound_tts.py               # Synthèse vocale browser et sons WAV (base64)
   ├── config.toml                # Configuration de l'environnement Streamlit
   ├── fix_css.py                 # Script de nettoyage et d'optimisation CSS
   ├── generate_references.py     # Générateur de courbes numpy (.npy) de référence
   ├── index.html                 # Landing page (serveur HTTP sur port 8000)
   ├── mailer.py                  # Envoi des e-mails d'invitation avec jetons d'activation
   ├── requirements.txt           # Liste des dépendances Python requises
   │
   ├── core/                      # Moteur d'analyse biomécanique
   │   ├── __init__.py
   │   ├── angle_calculator.py    # Trigonométrie et sélection des angles par exercice
   │   ├── comparator.py          # Scoring dynamique (FastDTW / Scipy)
   │   ├── pose_detector.py       # Wrapper de MediaPipe Pose
   │   ├── rag_engine.py          # Moteur de recherche sémantique s'appuyant sur FAISS
   │   └── report_generator.py    # Générateur de comptes-rendus cliniques au format PDF
   │
   ├── data/                      # Stockage des modèles et bases locales
   │   ├── protocols/             # Fichiers textes contenant les protocoles cliniques HAS
   │   ├── rag_index/             # Index vectoriel FAISS généré par sentence-transformers
   │   └── references/            # Fichiers .npy des mouvements types
   │
   ├── pages/                     # Espace professionnel
   │   ├── 1_Dashboard_Kine.py    # Tableau de bord clinique complet du Kinésithérapeute
   │   └── 2_Rapport_PDF.py       # Vue de génération et de téléchargement du rapport
   │
   └── scripts/
       └── build_rag_index.py     # Script d'indexation vectorielle des fichiers .txt

----

3. Dépendances Techniques Majeures
----------------------------------

KineAssist repose sur un ensemble de bibliothèques Python modernes, robustes et documentées :

*  **Interface & Web** :
   *  `streamlit` : Utilisé pour la construction des interfaces interactives (Patient et Kiné).
   *  `Jinja2` et serveurs HTTP standards pour la Landing Page.

*  **Vision par Ordinateur** :
   *  `mediapipe` : Solution de Google pour l'estimation en temps réel de la pose corporelle.
   *  `opencv-python-headless` : Capture du flux webcam, manipulation matricielle d'images et surcharges graphiques de repères.

*  **Traitement Numérique & Algorithmes** :
   *  `numpy` : Structure de données matricielle, traitement du signal des angles articulaires et lecture/écriture des trajectoires de référence.
   *  `fastdtw` & `scipy` : Implémentation du Dynamic Time Warping pour aligner et évaluer deux séries temporelles de longueurs différentes.

*  **Recherche Sémantique (RAG)** :
   *  `sentence-transformers` : Encodage de phrases en vecteurs denses en s'appuyant sur le modèle pré-entraîné léger `all-MiniLM-L6-v2`.
   *  `faiss-cpu` : Recherche de plus proches voisins par similarité cosinus développée par Meta AI.

*  **Sécurité & Reporting** :
   *  `bcrypt` : Hachage sécurisé des mots de passe.
   *  `reportlab` : Rendu programmatique de documents PDF vectoriels de qualité professionnelle.
