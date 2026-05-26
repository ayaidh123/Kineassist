Moteur RAG Local & Recherche Vectorielle
=========================================

Le moteur de recherche s'appuyant sur la génération augmentée par récupération (**RAG - Retrieval-Augmented Generation**) de **KineAssist** permet d'associer des retours cliniques de haute précision aux mouvements du patient, de manière décentralisée.

----

1. La Philosophie du RAG Local
------------------------------

Dans la plupart des architectures RAG classiques, les questions des utilisateurs sont envoyées à des APIs d'LLMs (comme OpenAI, Anthropic) qui retournent la réponse après traitement dans le Cloud. 

Pour KineAssist, cette approche présentait des verrous cliniques et légaux majeurs :

*  🔒 **Confidentialité absolue** : Les données cinétiques, les pathologies et les images vidéo d'un patient sont hautement sensibles. Elles ne doivent jamais transiter vers des serveurs tiers.
*  🔒 **Fonctionnement hors-ligne** : Une rééducation doit pouvoir s'effectuer sans dépendance à des APIs payantes ou à une connexion internet haut débit constante.
*  🔒 **Déterminisme médical** : Contrairement aux LLMs génératifs sujets aux hallucinations, KineAssist extrait des phrases exactes et vérifiées issues de consensus médicaux (Directives de la HAS).

La recherche sémantique est donc **100% locale**, utilisant des représentations vectorielles denses calculées sur la machine du patient.

----

2. Le Pipeline d'Indexation (`scripts/build_rag_index.py`)
-----------------------------------------------------------

L'indexation de la base de connaissances s'effectue en trois étapes :

.. figure:: ../assets/logoKine.png
   :alt: KineAssist Logo
   :align: right
   :width: 80px

1. **Chargement et Découpage (Chunking)** :
   Les documents cliniques officiels rédigés en français (`data/protocols/*.txt`) décrivant les thérapies post-LCA, coiffe des rotateurs, capsulites et mobilisation du rachis lombaire sont chargés. Ils sont segmentés en morceaux (*chunks*) de 400 mots avec un chevauchement (*overlap*) de 60 mots pour conserver le contexte aux frontières.

2. **Calcul des Représentations Vectorielles (Embeddings)** :
   Chaque chunk est encodé sous forme de vecteur dense à l'aide de la bibliothèque ``sentence-transformers`` et du modèle pré-entraîné léger **``all-MiniLM-L6-v2``** :
   
   .. code-block:: python

      from sentence_transformers import SentenceTransformer
      model = SentenceTransformer("all-MiniLM-L6-v2")
      embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)

   Ce modèle projette le sens sémantique de chaque phrase dans un espace vectoriel à **384 dimensions**.

3. **Construction de l'Index Vectoriel** :
   Les vecteurs denses sont normalisés selon la norme L2 pour calculer directement la similarité cosinus. Ils sont ensuite chargés dans un index flat **FAISS** :
   
   .. code-block:: python

       import faiss
       dim = embeddings.shape[1]
       index = faiss.IndexFlatIP(dim)
       faiss.normalize_L2(embeddings)
       index.add(embeddings)
       faiss.write_index(index, "data/rag_index/medical.index")

L'index FAISS et les chunks originaux sont sérialisés localement dans ``data/rag_index/``.

----

3. Recherche Sémantique & Suggestions de Correction (`core/rag_engine.py`)
--------------------------------------------------------------------------

Durant l'exécution des exercices par le patient, le flux de détection de mouvements identifie les écarts articulaires par rapport aux cibles presrites (ex: genou gauche trop peu fléchi de $24^\circ$).

Le moteur RAG s'active :

1. **Requête sémantique** :
   Une requête naturelle est construite à partir des erreurs détectées : 
   *"correction flexion genou gauche amplitude insuffisante cible 90 degres"*

2. **Recherche de Proximité Cosinus** :
   Le moteur convertit cette requête en vecteur de 384 dimensions et recherche les 3 chunks les plus similaires dans l'index FAISS :
   
   .. code-block:: python

      vec = self.embedder.encode([query]).astype(np.float32)
      faiss.normalize_L2(vec)
      scores, indices = self.index.search(vec, k=3)

3. **Extraction & Rendu** :
   Les phrases les plus pertinentes des documents HAS correspondants sont extraites et injectées instantanément à l'écran du patient pour guider son effort de correction.

----

4. Base de Règles Médicales de Secours (Fallback)
-------------------------------------------------

Si les dépendances vectorielles (`faiss-cpu`, `sentence-transformers`) ne sont pas installées ou si l'index n'a pas été généré localement, la classe ``RAGEngine`` bascule de manière transparente sur un **mode de secours (fallback)** :

*  Le système utilise un dictionnaire de règles prédéfinies (la constante ``RULES`` dans ``core/rag_engine.py``).
*  Ces règles recouvrent l'intégralité des combinaisons d'exercices, d'articulations et de directions d'erreurs (flexion insuffisante, flexion excessive, rotation compensatoire, etc.).
*  Le patient reçoit ainsi des consignes de correction toujours adaptées, garantissant la fiabilité clinique de KineAssist en toutes circonstances.
