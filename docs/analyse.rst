Analyse du Mouvement & Algorithmes
==================================

L'analyse de mouvement en temps réel constitue le cœur de l'innovation technologique de **KineAssist**. Grâce à des algorithmes de vision par ordinateur et de traitement du signal, l'application évalue la posture, compte les répétitions et attribue un score de précision biomécanique objectif.

----

1. Estimation de la Posture avec MediaPipe Pose
------------------------------------------------

KineAssist utilise le framework de Deep Learning **MediaPipe Pose** développé par Google pour extraire les repères corporels tridimensionnels du patient en temps réel.

.. figure:: ../assets/logoKine.png
   :alt: KineAssist Logo
   :align: right
   :width: 80px

Le modèle identifie **33 points clés** (landmarks) sur l'ensemble du corps humain :
*  Chaque point clé est caractérisé par ses coordonnées spatiales normalisées $(x, y, z)$ et un score de confiance (visibilité).
*  Les points clés cruciaux pour la rééducation motrice incluent : les épaules (points 11 et 12), les coudes (13 et 14), les hanches (23 et 24), les genoux (25 et 26) et les chevilles (27 et 28).

Wrapper PoseDetector (`core/pose_detector.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Ce module encapsule l'API MediaPipe :
1. **Initialisation** : Configuration des seuils de confiance de détection et de suivi (`min_detection_confidence`, `min_tracking_confidence`) et de la complexité du modèle (fixée à 1 pour garantir un bon équilibre entre précision et vitesse en temps réel).
2. **Process Frame** : Reçoit une image issue de la webcam au format BGR d'OpenCV, la convertit en RVB, puis exécute l'estimation de posture.
3. **Annotations graphiques** : Dessine les repères squelettiques et les connexions articulaires sur le flux vidéo, colorant les articulations clés en fonction de la justesse posturale (Vert = Excellent, Orange = Tolérance franchie, Rouge = Critique).

----

2. Calcul Trigonométrique des Angles Articulaires
-------------------------------------------------

Les coordonnées brutes extraites par MediaPipe sont exploitées dans ``core/angle_calculator.py`` afin d'obtenir la valeur angulaire instantanée des articulations clés.

L'angle $\theta$ formé par trois repères $A$, $B$ (le sommet de l'articulation) et $C$ est déterminé à partir de leurs coordonnées 2D projetées :

1. Calcul des vecteurs :

   $$\vec{BA} = A - B \quad \text{et} \quad \vec{BC} = C - B$$

2. Produit scalaire normalisé :

   $$\cos(\theta) = \frac{\vec{BA} \cdot \vec{BC}}{\|\vec{BA}\| \times \|\vec{BC}\| + \epsilon}$$

   *(avec $\epsilon = 10^{-6}$ pour éviter la division par zéro).*

3. Extraction de l'angle en degrés :

   $$\theta = \arccos(\cos(\theta)) \times \frac{180}{\pi}$$

Exemple d'implémentation en Python :

.. code-block:: python

   import numpy as np

   def calculate_angle(a, b, c):
       a = np.array(a[:2])
       b = np.array(b[:2])
       c = np.array(c[:2])
       ba = a - b
       bc = c - b
       cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
       cosine = np.clip(cosine, -1.0, 1.0)
       return round(float(np.degrees(np.arccos(cosine))), 1)

----

3. Automate Temporel de Détection des Répétitions
-------------------------------------------------

Pour valider le passage d'une répétition à la suivante, KineAssist s'appuie sur un automate à états finis basé sur des seuils angulaires limites dans ``app.py``.

Prenons l'exemple d'une **flexion du genou** :
*  **État Initial (Rep Inactive)** : Le patient a la jambe tendue ($\text{angle du genou} > 155^\circ$).
*  **Début de Répétition** : Lorsque l'angle du genou descend sous le seuil de flexion de $120^\circ$, la répétition est détectée "En cours". Les coordonnées angulaires successives commencent à être enregistrées dans un tampon d'analyse.
*  **Fin de Répétition** : Dès que l'angle remonte et franchit de nouveau le seuil d'extension complète ($155^\circ$), la répétition est validée comme "Terminée".
*  **Traitement** : Le signal enregistré dans le tampon est envoyé au module de scoring, et le compteur de répétitions est incrémenté de 1.

----

4. Scoring par Dynamic Time Warping (DTW)
-----------------------------------------

Comparer la performance du patient à un modèle type pose un défi majeur : chaque individu effectue le mouvement à son propre rythme (plus ou moins lentement). Une simple comparaison point à point (distance euclidienne classique) est inefficace.

KineAssist intègre l'algorithme **Dynamic Time Warping (DTW)** via le module ``core/comparator.py`` pour résoudre ce problème. Le DTW permet de trouver l'alignement temporel optimal entre deux séries de longueurs différentes (la répétition du patient contre la courbe idéale issue de ``generate_references.py``).

Le score final est déduit de la distance minimale d'alignement normalisée :

.. code-block:: python

   from fastdtw import fastdtw
   from scipy.spatial.distance import euclidean

   # ... Nettoyage et normalisation des dimensions articulaires ...
   dist, _ = fastdtw(current, ref, dist=euclidean)
   
   # Normalisation par la longueur maximale des trajectoires et le nombre de joints suivis
   normalized_dist = dist / (max(len(current), len(ref)) * n_joints + 1e-6)
   
   # Conversion en score sur 100
   score = max(0.0, 100.0 - normalized_dist * 1.8)
