import streamlit as st
from scraper.jumia_scraper import search_jumia
from model.predictor import predict_category

# ----------------------------
# Configuration de la page
# ----------------------------
st.set_page_config(
    page_title="EcoSort-Search",
    page_icon="♻️",
    layout="wide",
)

# ----------------------------
# CSS personnalisé
# ----------------------------
st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .product-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        transition: box-shadow 0.2s;
    }
    .product-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .result-box {
        padding: 40px;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# État de session (historique)
# ----------------------------
if "historique" not in st.session_state:
    st.session_state["historique"] = []
if "resultats" not in st.session_state:
    st.session_state["resultats"] = []
if "produit_choisi" not in st.session_state:
    st.session_state["produit_choisi"] = None

# ----------------------------
# Sidebar : légende des poubelles
# ----------------------------
with st.sidebar:
    st.header("🗑️ Légende du tri")
    legende = [
        ("🟡 Poubelle Jaune", "Plastique, métal, carton"),
        ("🟢 Poubelle Verte", "Verre"),
        ("🔵 Poubelle Bleue", "Papier"),
        ("🎛️ Bac D3E", "Électronique"),
        ("⚫ Poubelle Marron", "Déchets résiduels"),
    ]
    for titre, desc in legende:
        st.markdown(f"**{titre}**")
        st.caption(desc)

    st.divider()
    st.header("🕘 Historique")
    if st.session_state["historique"]:
        for item in reversed(st.session_state["historique"][-5:]):
            st.caption(f"{item['nom']} → {item['poubelle']}")
    else:
        st.caption("Aucune recherche pour le moment.")

    if st.button("🗑️ Effacer l'historique"):
        st.session_state["historique"] = []
        st.rerun()

# ----------------------------
# En-tête principal
# ----------------------------
st.markdown('<p class="main-title">♻️ EcoSort-Search</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Entrez le nom d\'un produit pour connaître sa consigne de tri</p>',
    unsafe_allow_html=True,
)

# ----------------------------
# Barre de recherche
# ----------------------------
col_input, col_btn = st.columns([4, 1])
with col_input:
    query = st.text_input(
        "Nom du produit", placeholder="ex: shampoing Dove", label_visibility="collapsed"
    )
with col_btn:
    rechercher = st.button("🔍 Rechercher", use_container_width=True)

if rechercher and query:
    with st.spinner(f"Recherche de « {query} » sur Jumia..."):
        st.session_state["resultats"] = search_jumia(query)
    st.session_state["produit_choisi"] = None

elif rechercher and not query:
    st.warning("Merci d'entrer un nom de produit avant de lancer la recherche.")

# ----------------------------
# Affichage des résultats (horizontal, scrollable)
# ----------------------------
if st.session_state["resultats"]:
    st.subheader(f"📦 {len(st.session_state['resultats'])} résultats trouvés")

    cards_html = '<div style="display:flex; overflow-x:auto; gap:16px; padding:10px 5px;">'
    for produit in st.session_state["resultats"]:
        cards_html += f"""
        <div style="flex:0 0 180px; border:1px solid #e0e0e0; border-radius:12px;
                    padding:12px; text-align:center; background:white;">
            <img src="{produit['image_url']}" style="width:100%; height:120px;
                 object-fit:cover; border-radius:8px;" />
            <p style="font-weight:600; margin:8px 0 4px 0; font-size:0.9rem;">{produit['nom']}</p>
            <p style="color:#666; font-size:0.85rem; margin:0;">{produit.get('prix', '')}</p>
        </div>
        """
    cards_html += "</div>"

    st.markdown(cards_html, unsafe_allow_html=True)

    # Sélection du produit (les boutons ne peuvent pas être insérés dans le HTML brut ci-dessus)
    noms_produits = [p["nom"] for p in st.session_state["resultats"]]
    choix_nom = st.selectbox("Sélectionner le produit à analyser :", noms_produits)

    if st.button("✅ Analyser ce produit", use_container_width=True):
        st.session_state["produit_choisi"] = next(
            p for p in st.session_state["resultats"] if p["nom"] == choix_nom
        )

# ----------------------------
# Analyse et résultat du tri
# ----------------------------
if st.session_state["produit_choisi"]:
    produit = st.session_state["produit_choisi"]
    st.divider()
    st.subheader(f"🔬 Analyse de : {produit['nom']}")

    with st.spinner("Analyse par l'IA en cours..."):
        prediction = predict_category(produit["image_url"])

    # Ajout à l'historique (une seule fois par choix)
    if not st.session_state["historique"] or st.session_state["historique"][-1]["nom"] != produit["nom"]:
        st.session_state["historique"].append(
            {"nom": produit["nom"], "poubelle": prediction["poubelle"]}
        )

    couleur = prediction["couleur"]
    confiance_pct = int(prediction["confiance"] * 100)

    st.markdown(
        f"""
        <div class="result-box" style="background-color:{couleur};">
            <h1>Poubelle {prediction['poubelle']}</h1>
            <p style="font-size:1.1rem;">Matière détectée : <b>{prediction['classe']}</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("**Confiance du modèle :**")
    st.progress(prediction["confiance"], text=f"{confiance_pct}%")

    if st.button("🔄 Nouvelle recherche"):
        st.session_state["resultats"] = []
        st.session_state["produit_choisi"] = None
        st.rerun()