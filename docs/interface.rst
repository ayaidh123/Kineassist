Interfaces & Design Visuel
==========================

L'expérience utilisateur de **KineAssist** a été soigneusement élaborée pour offrir une esthétique soignée, s'affranchissant du style Streamlit par défaut au profit d'un design moderne, vivant et fluide.

----

1. Portail Kinésithérapeute (`pages/1_Dashboard_Kine.py`)
---------------------------------------------------------

Destiné aux professionnels, ce portail sert de cockpit clinique. Il intègre :

.. figure:: ../assets/logoKine.png
   :alt: KineAssist Logo
   :align: right
   :width: 80px

*  **Tableau de bord de monitoring** : Synthèse visuelle de l'état de chaque patient (semaine de rééducation en cours, nombre d'entraînements validés par rapport à l'objectif de prescription, moyenne des scores).
*  **Graphique d'évolution hebdomadaire** : Un tracé vectoriel des performances moyennes et maximales au fil des séances pour objectiver le progrès clinique.
*  **Fiches patients interactives** : Formulaires fluides permettant de mettre à jour la pathologie, l'exercice prescrit, la semaine de rééducation en cours, de consigner des notes d'évolution et d'activer des indicateurs visuels d'alerte en cas de baisse sensible des résultats.
*  **Système d'invitation et d'activation** : Interface simplifiée pour enregistrer et inviter par courriel de nouveaux patients en générant un jeton sécurisé.
*  **Espace de planification** : Permet au kinésithérapeute d'ajouter des rendez-vous en cabinet.

----

2. Portail Patient (`app.py`)
-----------------------------

L'interface dédiée au patient privilégie la simplicité, la clarté et l'engagement :

*  **Tableau de bord de synthèse** : Rappel clair du programme prescrit pour la semaine, de l'état de complétion de l'objectif hebdomadaire (jauge de progression) et historique détaillé des dernières séances.
*  **Session interactive guidée** :
   *  **Flux vidéo annoté** : Dessine les repères squelettiques et les cercles articulaires colorés selon la justesse posturale (Vert = Correct, Orange = Tolérance franchie, Rouge = Écart critique).
   *  **Zone de retour (Feedback)** : Affiche des messages de correction issus du moteur RAG en superposition semi-transparente directement sur l'image.
   *  **Panneau latéral de métriques** : Visualisation en temps réel du nombre de répétitions effectuées, du score moyen et de l'état d'activité de la caméra.

----

3. Design Système & Customisation CSS
--------------------------------------

L'esthétique de KineAssist s'appuie sur une surcharge CSS poussée injectée via le markdown de Streamlit (fonction ``apply_theme``) :

*  **Typographie Moderne** : Intégration de la police Google Font **Sora** pour la structure globale et les titres, et **JetBrains Mono** pour les affichages numériques de scores et de répétitions.
*  **Thème Double Premium** :
   *  **Mode Clair (Teal & Pure White)** : Fond épuré gris très clair (`#F8F9FB`), surfaces blanches immaculées (`#FFFFFF`), bordures fines douces et accents de couleur sarcelle (teal, `#0d9488`).
   *  **Mode Sombre (Deep Navy)** : Fond bleu nuit profond (`#0A0E19`), surfaces sombres contrastées (`#111827`) pour réduire la fatigue visuelle lors des séances en intérieur.
*  **Composants graphiques surchargés** :
   *  *Formulaires et Inputs* : Coins arrondis de $12\text{px}$, arrières-plans neutres, surbrillance au focus.
   *  *Boutons* : Boutons d'action sombres et contrastés pour le profil Kiné, et teal pour le profil Patient, avec des micro-animations fluides de transition.
   *  *Popups sémantiques* : Bulles de conseils RAG avec une bordure gauche colorée de $4\text{px}$ identifiant la sévérité (Rouge pour les alertes critiques, Noir/Teal pour les conseils modérés).

----

4. Retour Audio Multisensoriel (`sound_tts.py`)
-----------------------------------------------

Afin de permettre au patient de corriger sa posture sans devoir fixer constamment l'écran, KineAssist intègre une rétroaction audio complète :

Sons WAV intégrés
~~~~~~~~~~~~~~~~~
Des fichiers audio compacts sont stockés dans le projet, encodés en **Base64** dans ``sound_tts.py`` et décodés à la volée dans le navigateur via une balise JavaScript ``<audio>`` :
*  **Ding aigu et brillant (`sound_good.wav`)** : Se déclenche à la validation de chaque répétition correcte pour encourager le patient.
*  **Signal sonore descendant et grave (`sound_error.wav`)** : Avertit le patient en cas de mouvement compensatoire dangereux ou de mauvaise posture prolongée.

Synthèse Vocale Native (TTS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Le système tire parti de la **Web Speech API** intégrée nativement dans tous les navigateurs modernes. Sans nécessiter de requêtes réseau ni de synthèse de voix Cloud (comme Google Cloud TTS ou ElevenLabs), KineAssist prononce des consignes claires en français :
*  Annonce à voix haute du numéro de répétition validé (*"Répétition 3"*).
*  Lecture vocale des alertes critiques issues du moteur RAG pour guider l'ajustement physique immédiat (*"Veuillez fléchir davantage le genou droit"*).

Exemple d'injection JS pour la synthèse vocale :

.. code-block:: python

   def speak(text: str, lang: str = "fr-FR", rate: float = 1.0):
       text_safe = text.replace("'", " ").replace('"', ' ').replace("\n", " ")[:200]
       html = f"""
       <script>
       (function(){{
           try {{
               window.speechSynthesis.cancel();
               const u = new SpeechSynthesisUtterance('{text_safe}');
               u.lang  = '{lang}';
               u.rate  = {rate};
               window.speechSynthesis.speak(u);
           }} catch(e) {{}}
       }})();
       </script>
       """
       components.html(html, height=0)
