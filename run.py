

import os
import streamlit as st
import streamlit.components.v1 as components

# ── Config de la page ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KineAssist",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Masquer la sidebar et le header Streamlit sur la landing ─────────────────
st.markdown(
    """
    <style>
        [data-testid="stSidebar"]        { display: none; }
        [data-testid="stHeader"]         { display: none; }
        [data-testid="stToolbar"]        { display: none; }
        .block-container                 { padding: 0 !important; }
        footer                           { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Lecture du fichier index.html ─────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")

if not os.path.exists(INDEX_PATH):
    st.error(
        "⚠️ Fichier `index.html` introuvable à la racine du projet. "
        "Vérifiez que le fichier est bien commité dans votre dépôt GitHub."
    )
    st.stop()

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

# ── Injection d'un bouton Streamlit dans l'HTML pour la navigation ────────────
# On injecte un script postMessage pour que le bouton HTML natif
# puisse déclencher la navigation Streamlit vers app.py.
BRIDGE_SCRIPT = """
<script>
  // Cherche tous les éléments portant data-streamlit-nav
  document.querySelectorAll('[data-streamlit-nav]').forEach(function(el) {
    el.addEventListener('click', function(e) {
      e.preventDefault();
      // Envoie un message à Streamlit pour changer de page
      window.parent.postMessage(
        { type: 'streamlit:navigate', page: el.dataset.streamlitNav },
        '*'
      );
    });
  });
</script>
"""

# Insère le script pont juste avant </body>
if "</body>" in html_content:
    html_content = html_content.replace("</body>", BRIDGE_SCRIPT + "</body>")
else:
    html_content += BRIDGE_SCRIPT

# ── Affichage de la Landing Page ──────────────────────────────────────────────
components.html(html_content, height=900, scrolling=True)

# ── Bouton de secours Streamlit natif (toujours visible) ─────────────────────
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(
        "🚀 Accéder à l'Application KineAssist",
        use_container_width=True,
        type="primary",
    ):
        st.switch_page("app.py")