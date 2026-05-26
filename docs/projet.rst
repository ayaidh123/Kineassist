Le Projet KineAssist
====================

.. figure:: ../assets/logoKine.png
   :alt: KineAssist Logo
   :align: left
   :width: 100px

**KineAssist** est une plateforme web interactive d'intelligence artificielle conçue pour moderniser le suivi de la rééducation motrice et orthopédique à domicile. 

En combinant estimation de posture en temps réel, comparaison sémantique de courbes de mouvement et conseils issus des référentiels cliniques, KineAssist offre un canal de communication bidirectionnel et sécurisé entre le kinésithérapeute et le patient.

----

1. Contexte & Motivation
------------------------

La rééducation fonctionnelle constitue un pilier majeur de la récupération après un traumatisme orthopédique (ex: rupture du ligament croisé antérieur, fracture), une intervention chirurgicale ou un accident vasculaire cérébral (AVC). Cependant, l'efficacité de ce processus dépend fortement de la régularité et de la qualité des exercices exécutés par le patient en dehors des séances au cabinet médical. 

Les praticiens font face à plusieurs défis majeurs dans le suivi à domicile :

*  ⚠️ **L'absence de visibilité** : Le praticien ne dispose d'aucun moyen objectif de quantifier l'observance thérapeutique du patient ou la régularité de son travail entre deux consultations.
*  ⚠️ **Le manque de guidage actif** : Sans superviseur, le patient exécute souvent ses mouvements de manière approximative, ce qui limite le progrès thérapeutique ou, pire, aggrave la pathologie initiale par compensation biomécanique.
*  ⚠️ **La perte de motivation** : Le manque de retour (feedback) immédiat sur les efforts fournis engendre un fort taux d'abandon du programme d'exercices à domicile.
*  ⚠️ **La confidentialité des données** : Les solutions de vision par ordinateur reposent souvent sur le Cloud, ce qui soulève d'importantes questions éthiques et légales quant au traitement des flux vidéo contenant des visages et des corps de patients.

KineAssist a été conçu pour lever l'ensemble de ces verrous technologiques et cliniques.

----

2. La Solution KineAssist
-------------------------

KineAssist introduit une approche d'**intelligence artificielle décentralisée et respectueuse de la vie privée**, où l'intégralité du traitement vidéo et de l'analyse sémantique est exécutée **localement dans le navigateur du patient**.

La plateforme se décline sous deux profils d'utilisateurs distincts :

Le Portail du Kinésithérapeute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Un espace clinique permettant au praticien de :
*  **Gérer son portefeuille de patients** de manière centralisée.
*  **Prescrire des protocoles personnalisés** (nombre de séries, répétitions cibles, type d'exercices) adaptés à la pathologie et à la semaine de rééducation.
*  **Consulter les tableaux de bord d'observance** (tendance des scores, répétitions effectuées, évolution hebdomadaire).
*  **Consigner des observations et notes cliniques** au fil de l'évolution du patient.

Le Portail du Patient
~~~~~~~~~~~~~~~~~~~~~
Une interface ergonomique et intuitive qui guide le patient au quotidien :
*  **Accès au protocole prescrit** pour la semaine en cours.
*  **Session interactive avec caméra** : Le patient effectue ses mouvements face à sa webcam. L'IA estime sa posture, compte ses répétitions en temps réel et calcule un score de précision.
*  **Retour d'effort multisensoriel** : Un retour visuel (repères colorés sur les articulations) et un retour vocal (synthèse vocale) guident le patient pour corriger immédiatement ses défauts d'alignement.
*  **Historique et progression** : Visualisation claire des succès passés pour soutenir la motivation.
