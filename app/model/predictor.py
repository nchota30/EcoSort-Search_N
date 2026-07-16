import random

# Mapping officiel classe -> poubelle (à garder, sera réutilisé par le vrai modèle)
CLASSE_VERS_POUBELLE = {
    "plastic": {"poubelle": "JAUNE", "couleur": "#FFD700"},
    "metal": {"poubelle": "JAUNE", "couleur": "#FFD700"},
    "cardboard": {"poubelle": "JAUNE", "couleur": "#FFD700"},
    "glass": {"poubelle": "VERTE", "couleur": "#228B22"},
    "paper": {"poubelle": "BLEUE", "couleur": "#1E90FF"},
    "trash": {"poubelle": "MARRON", "couleur": "#5C4033"},
}


def predict_category(image_path_or_url: str) -> dict:
    """
    MOCK temporaire - à remplacer par le vrai modèle .h5 de l'équipe.
    Retourne une prédiction aléatoire respectant le contrat d'interface.
    """
    classe = random.choice(list(CLASSE_VERS_POUBELLE.keys()))
    info = CLASSE_VERS_POUBELLE[classe]
    return {
        "classe": classe,
        "confiance": round(random.uniform(0.75, 0.99), 2),
        "poubelle": info["poubelle"],
        "couleur": info["couleur"],
    }