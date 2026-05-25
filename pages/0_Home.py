import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="KineAssist",
    page_icon="assets/logoKine.png",
    layout="wide"
)

# Cacher la toolbar et le menu Streamlit
st.markdown("""
    <style>
    #MainMenu, footer, header,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stSidebarNav"] { display:none !important; }
    .block-container { padding: 0 !important; }
    iframe { border: none; }
    </style>
""", unsafe_allow_html=True)

# Lire index.html
html_path = Path("index.html")
if html_path.exists():
    html_content = html_path.read_text(encoding="utf-8")

    # Remplacer les liens vers Streamlit par des liens internes
    # Les boutons Connexion/Commencer redirigent vers app.py (page Patient)
    html_content = html_content.replace(
        'href="https://kineassist.streamlit.app"',
        'href="javascript:void(0)" onclick="window.parent.postMessage({type:\'streamlit:setComponentValue\', value:\'go_app\'}, \'*\')"'
    )

    components.html(html_content, height=4000, scrolling=True)
else:
    st.error("index.html introuvable.")
