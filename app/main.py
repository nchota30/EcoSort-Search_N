import streamlit as st
import requests
from io import BytesIO
from PIL import Image
from scraper.jumia_scraper import rechercher_top5
from model.predictor import EcoSortPredictor

# ----------------------------
# Configuration de la page
# ----------------------------
st.set_page_config(
    page_title="EcoSort-Search",
    page_icon="♻️",
    layout="wide",
)

@st.cache_resource
def get_predictor():
    return EcoSortPredictor()

predictor = get_predictor()

# ----------------------------
# CSS : thème sombre / néon / tech
# ----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Rubik:wght@300;400;600&display=swap');

    .stApp {
        background: radial-gradient(circle at 20% 0%, #131A2B 0%, #0A0E17 60%);
    }

    * {
        font-family: 'Rubik', sans-serif;
    }

    .main-title {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00F5D4, #7B2FF7, #00F5D4);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 4s linear infinite;
        margin-bottom: 0;
        text-shadow: 0 0 30px rgba(0, 245, 212, 0.2);
    }

    @keyframes shine {
        to { background-position: 200% center; }
    }

    .subtitle {
        text-align: center;
        color: #8A93A8;
        font-size: 1.05rem;
        margin-bottom: 2.5rem;
        letter-spacing: 0.5px;
    }

    /* Champ de recherche */
    .stTextInput input {
        background-color: rgba(19, 26, 43, 0.8) !important;
        border: 1px solid rgba(0, 245, 212, 0.3) !important;
        border-radius: 12px !important;
        color: #E8E8E8 !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border: 1px solid #00F5D4 !important;
        box-shadow: 0 0 20px rgba(0, 245, 212, 0.3) !important;
    }

    /* Boutons */
    .stButton button {
        background: linear-gradient(135deg, #00F5D4, #7B2FF7) !important;
        color: #0A0E17 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 0 15px rgba(0, 245, 212, 0.25);
    }
    .stButton button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 0 25px rgba(0, 245, 212, 0.5);
    }

    /* Cartes produits */
    .product-card {
        flex: 0 0 190px;
        border: 1px solid rgba(0, 245, 212, 0.15);
        border-radius: 16px;
        padding: 14px;
        text-align: center;
        background: rgba(19, 26, 43, 0.6);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        cursor: default;
    }
    .product-card:hover {
        border: 1px solid #00F5D4;
        box-shadow: 0 0 25px rgba(0, 245, 212, 0.25);
        transform: translateY(-4px);
    }
    .product-card img {
        border-radius: 10px;
        width: 100%;
        height: 130px;
        object-fit: cover;
    }
    .product-name {
        font-weight: 600;
        margin: 10px 0 4px 0;
        font-size: 0.9rem;
        color: #E8E8E8;
    }
    .product-price {
        color: #00F5D4;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0;
    }

    /* Boîte de résultat final */
    .result-box {
        padding: 45px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-top: 25px;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease;
        box-shadow: 0 0 40px rgba(0,0,0,0.4);
    }
    .result-box h1 {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.2rem;
        margin-bottom: 10px;
        text-shadow: 0 0 20px rgba(255,255,255,0.4);
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F1522 0%, #0A0E17 100%);
        border-right: 1px solid rgba(0, 245, 212, 0.1);
    }

    hr {
        border-color: rgba(0, 245, 212, 0.15) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# État de session
# ----------------------------
if "historique" not in st.session_state:
    st.session_state["historique"] = []
if "resultats" not in st.session_state:
    st.session_state["resultats"] = []
if "produit_choisi" not in st.session_state:
    st.session_state["produit_choisi"] = None

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.markdown("### 🗑️ Légende du tri")
    legende = [
        ("🟡", "Poubelle Jaune", "Plastique, métal, carton"),
        ("🟢", "Poubelle Verte", "Verre"),
        ("🔵", "Poubelle Bleue", "Papier"),
        ("🎛️", "Bac D3E", "Électronique"),
        ("⚫", "Poubelle Marron", "Déchets résiduels"),
    ]
    for emoji, titre, desc in legende:
        st.markdown(f"**{emoji} {titre}**")
        st.caption(desc)

    st.divider()
    st.markdown("### 🕘 Historique")
    if st.session_state["historique"]:
        for item in reversed(st.session_state["historique"][-5:]):
            st.caption(f"▸ {item['nom'][:30]} → **{item['poubelle']}**")
    else:
        st.caption("Aucune recherche pour le moment.")

    if st.button("Effacer l'historique", use_container_width=True):
        st.session_state["historique"] = []
        st.rerun()

# ----------------------------
# En-tête
# ----------------------------
st.markdown('<p class="main-title">♻️ ECOSORT-SEARCH</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Intelligence artificielle · Tri sélectif intelligent</p>',
    unsafe_allow_html=True,
)

# ----------------------------
# Barre de recherche
# ----------------------------
col_input, col_btn = st.columns([4, 1])
with col_input:
    query = st.text_input(
        "Nom du produit", placeholder="🔍 ex: shampoing Dove, chargeur téléphone...",
        label_visibility="collapsed"
    )
with col_btn:
    rechercher = st.button("RECHERCHER", use_container_width=True)

if rechercher and query:
    with st.spinner(f"🛰️ Scan de « {query} » sur Jumia..."):
        st.session_state["resultats"] = rechercher_top5(query)
    st.session_state["produit_choisi"] = None
elif rechercher and not query:
    st.warning("Merci d'entrer un nom de produit avant de lancer la recherche.")

# ----------------------------
# Résultats (cartes horizontales)
# ----------------------------
if st.session_state["resultats"]:
    st.markdown(f"#### 📦 {len(st.session_state['resultats'])} résultats détectés")

    cards_html = '<div style="display:flex; overflow-x:auto; gap:16px; padding:10px 5px;">'
    for produit in st.session_state["resultats"]:
        cards_html += (
            f'<div class="product-card">'
            f'<img src="{produit["image_url"]}" />'
            f'<p class="product-name">{produit["nom"]}</p>'
            f'<p class="product-price">{produit.get("prix", "")}</p>'
            f'</div>'
        )
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

    noms_produits = [p["nom"] for p in st.session_state["resultats"]]
    choix_nom = st.selectbox("Sélectionner le produit à analyser :", noms_produits)

    if st.button("⚡ ANALYSER CE PRODUIT", use_container_width=True):
        st.session_state["produit_choisi"] = next(
            p for p in st.session_state["resultats"] if p["nom"] == choix_nom
        )

# ----------------------------
# Analyse et résultat
# ----------------------------
if st.session_state["produit_choisi"]:
    produit = st.session_state["produit_choisi"]
    st.divider()
    st.markdown(f"#### 🔬 Analyse de : {produit['nom']}")

    with st.spinner("🧠 Intelligence artificielle en cours d'analyse..."):
        try:
            response = requests.get(produit["image_url"], timeout=10)
            image = Image.open(BytesIO(response.content))
            prediction = predictor.predict(image, product_name=produit.get("nom", ""))
        except Exception as e:
            st.error(f"Impossible d'analyser ce produit : {e}")
            st.stop()

    if not st.session_state["historique"] or st.session_state["historique"][-1]["nom"] != produit["nom"]:
        st.session_state["historique"].append(
            {"nom": produit["nom"], "poubelle": prediction["label"]}
        )

    couleur = prediction["color"]
    matiere = prediction["raw_class"] or "Électronique (détecté par nom)"

    st.markdown(
        f"""
        <div class="result-box" style="background: linear-gradient(135deg, {couleur}dd, {couleur}88);">
            <h1>{prediction['label']}</h1>
            <p style="font-size:1.1rem; opacity:0.9;">Matière détectée : <b>{matiere}</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if prediction["confidence"] is not None:
        confiance_pct = int(prediction["confidence"] * 100)
        st.write("**Niveau de confiance du modèle :**")
        st.progress(prediction["confidence"], text=f"{confiance_pct}%")
    else:
        st.info("⚡ Produit électronique détecté directement par son nom (pas d'analyse d'image nécessaire).")

    if st.button("🔄 NOUVELLE RECHERCHE", use_container_width=True):
        st.session_state["resultats"] = []
        st.session_state["produit_choisi"] = None
        st.rerun()