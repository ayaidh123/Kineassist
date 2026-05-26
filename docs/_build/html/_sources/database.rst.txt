Schéma de la Base de Données
=============================

La persistance des données dans **KineAssist** s'appuie sur une base de données relationnelle locale **SQLite** gérée de manière dynamique. Le fichier de stockage est nommé ``kineassist.db``.

L'accès à la base de données est centralisé et sécurisé dans le module ``database.py``.

----

1. Architecture des Tables
--------------------------

Le schéma relationnel est modélisé pour lier de manière stricte les kinésithérapeutes, les patients qui leur sont affectés, les sessions d'entraînement réalisées et les invitations d'activation de comptes :

.. figure:: ../assets/logoKine.png
   :alt: KineAssist Logo
   :align: right
   :width: 80px

kines
~~~~~
Cette table contient les comptes des professionnels de santé.

*  ``id`` (INTEGER PRIMARY KEY AUTOINCREMENT) : Identifiant unique du kinésithérapeute.
*  ``email`` (TEXT UNIQUE NOT NULL) : Adresse e-mail servant d'identifiant de connexion (insensible à la casse).
*  ``nom`` (TEXT NOT NULL) : Nom complet du praticien.
*  ``password_hash`` (TEXT NOT NULL) : Hash sécurisé Bcrypt du mot de passe.
*  ``created_at`` (TEXT DEFAULT) : Date de création du compte.

patients
~~~~~~~~
Cette table stocke les fiches détaillées des patients. Chaque patient est obligatoirement rattaché à un kinésithérapeute référent.

*  ``id`` (INTEGER PRIMARY KEY AUTOINCREMENT) : Identifiant unique du patient.
*  ``email`` (TEXT UNIQUE NOT NULL) : Adresse e-mail du patient.
*  ``nom`` (TEXT NOT NULL) : Nom complet.
*  ``age`` (INTEGER DEFAULT 0) : Âge du patient.
*  ``pathologie`` (TEXT DEFAULT '') : Diagnostic médical consigné par le praticien.
*  ``exercice`` (TEXT DEFAULT) : Exercice principal prescrit.
*  ``protocol`` (TEXT DEFAULT '') : Protocole médical ou programme d'exercices complexe associé.
*  ``semaine`` (INTEGER DEFAULT 1) : Numéro de la semaine de rééducation active en cours.
*  ``objectif_semaine`` (INTEGER DEFAULT 8) : Nombre de sessions attendu par semaine.
*  ``password_hash`` (TEXT DEFAULT NULL) : Hash du mot de passe (défini à l'activation).
*  ``activated`` (INTEGER DEFAULT 0) : Drapeau d'activation (0 = invité, 1 = actif).
*  ``kine_id`` (INTEGER NOT NULL) : Clé étrangère pointant vers ``kines.id``.
*  ``notes`` (TEXT DEFAULT '') : Espace de notes cliniques pour le praticien.
*  ``alerte`` (INTEGER DEFAULT 0) : Indicateur d'inactivité ou de baisse de performance (1 = alerte active).
*  ``photo_b64`` (TEXT DEFAULT '') : Photo de profil encodée en base64 pour affichage.
*  ``poids`` (REAL DEFAULT 0) : Poids du patient en kg.
*  ``taille`` (INTEGER DEFAULT 0) : Taille en cm.
*  ``telephone`` (TEXT DEFAULT '') : Numéro de contact.
*  ``antecedents`` (TEXT DEFAULT '') : Antécédents médicaux déclarés par le patient.
*  ``genre`` (TEXT DEFAULT '') : Genre.

invitations
~~~~~~~~~~~
Gère les jetons (tokens) temporaires permettant d'activer les comptes patients de manière sécurisée sans stocker de mot de passe temporaire en clair.

*  ``id`` (INTEGER PRIMARY KEY AUTOINCREMENT) : Identifiant.
*  ``token`` (TEXT UNIQUE NOT NULL) : Jeton alphanumérique aléatoire sécurisé à sens unique (généré via ``secrets.token_urlsafe(32)``).
*  ``patient_id`` (INTEGER NOT NULL) : Identifiant du patient associé.
*  ``email`` (TEXT NOT NULL) : Adresse e-mail cible.
*  ``expires_at`` (TEXT NOT NULL) : Horodatage d'expiration du jeton (fixé à +72h après création).
*  ``used`` (INTEGER DEFAULT 0) : Drapeau d'utilisation (1 = consommé).

sessions_kine
~~~~~~~~~~~~~
Historique des sessions d'entraînement réalisées par le patient avec estimation automatique des performances.

*  ``id`` (INTEGER PRIMARY KEY AUTOINCREMENT) : Identifiant.
*  ``patient_id`` (INTEGER NOT NULL) : Identifiant du patient ayant exécuté la session.
*  ``date`` (TEXT NOT NULL) : Date de réalisation (au format ``JJ/MM/AAAA``).
*  ``exercice`` (TEXT DEFAULT '') : Intitulé de l'exercice effectué.
*  ``reps`` (INTEGER DEFAULT 0) : Nombre de répétitions validées.
*  ``score_mean`` (REAL DEFAULT 0) : Score de précision moyen calculé sur la session (sur 100).
*  ``score_best`` (REAL DEFAULT 0) : Meilleur score de répétition obtenu.
*  ``trend`` (TEXT DEFAULT 'stable') : Évolution de la performance (ex: 'amelioration', 'stable', 'baisse').
*  ``semaine`` (INTEGER DEFAULT 1) : Index de la semaine de rééducation au moment de l'exercice.

----

2. Sécurité & Hachage Cryptographique
-------------------------------------

KineAssist assure la confidentialité des mots de passe en évitant tout stockage en clair dans SQLite. 

Le module utilise la bibliothèque **Bcrypt** pour appliquer un hachage unidirectionnel lent renforcé par un sel cryptographique aléatoire. Cela protège la base contre les attaques par dictionnaire ou par tables arc-en-ciel.

Exemple d'implémentation dans ``database.py`` :

.. code-block:: python

   import bcrypt

   def _hash(password: str) -> str:
       """Hash un mot de passe avec un sel dynamique et retourne une chaine UTF-8."""
       return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

   def _check_pwd(plain: str, hashed: str) -> bool:
       """Vérifie la validité d'un mot de passe contre son empreinte hachée."""
       try:
           return bcrypt.checkpw(plain.encode(), hashed.encode())
       except Exception:
           return False

----

3. Processus d'Invitation & d'Activation du Patient
---------------------------------------------------

Pour inscrire un nouveau patient :
1. **Création** : Le kinésithérapeute enregistre le patient avec ses paramètres cliniques fondamentaux.
2. **Jeton d'activation** : Le système génère automatiquement un token de sécurité unique :
   
   .. code-block:: python

      import secrets
      from datetime import datetime, timedelta

      token = secrets.token_urlsafe(32)
      expires = (datetime.now() + timedelta(hours=72)).isoformat()
   
3. **Envoi par E-mail** : Un e-mail contenant le lien sécurisé (valable 72 heures) est envoyé au patient via ``mailer.py``.
4. **Activation** : Le patient clique sur le lien, saisit son mot de passe personnalisé, ce qui consomme le jeton et active son profil (champ ``activated = 1``).
