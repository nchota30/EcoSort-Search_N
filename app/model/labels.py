"""
labels.py
---------
Le dataset Kaggle "Garbage Classification" fournit 6 classes brutes :
cardboard, glass, metal, paper, plastic, trash.
ZEDZDEZEZFEFE
Le projet exige 5 catégories de tri officielles, dont le Bac Électronique
(D3E) qui N'EXISTE PAS dans le dataset image. Ce module centralise :

1. Le mapping classe brute -> catégorie officielle (couleur UI incluse)
2. Une détection D3E par mots-clés sur le NOM du produit scrapé
   (à appliquer AVANT même d'interroger le modèle image, car un
   chargeur ou un smartphone n'a pas de "texture matière" caractéristique
   exploitable par le CNN).
"""

# ----------------------------------------------------------------------
# 1) Mapping classe Kaggle -> catégorie officielle EcoSort
# ----------------------------------------------------------------------
CLASS_TO_BIN = {
    "plastic":   {"bin": "JAUNE",  "label": "Poubelle JAUNE",         "color": "#FFD500"},
    "metal":     {"bin": "JAUNE",  "label": "Poubelle JAUNE",         "color": "#FFD500"},
    "cardboard": {"bin": "JAUNE",  "label": "Poubelle JAUNE",         "color": "#FFD500"},
    "glass":     {"bin": "VERTE",  "label": "Poubelle VERTE",         "color": "#2E8B57"},
    "paper":     {"bin": "BLEUE",  "label": "Poubelle BLEUE",         "color": "#1E90FF"},
    "battery":   {"bin": "D3E",    "label": "Bac Électronique (D3E)",         "color": "#808080"},
    "trash":     {"bin": "MARRON", "label": "Poubelle MARRON / NOIRE","color": "#5C4033"},
    "biological":{"bin": "MARRON", "label": "Poubelle MARRON / NOIRE","color": "#5C4033"},
    "clothes":   {"bin": "MARRON", "label": "Poubelle MARRON / NOIRE","color": "#5C4033"},
    "shoes":     {"bin": "MARRON", "label": "Poubelle MARRON / NOIRE","color": "#5C4033"},
} 

# Catégorie D3E, ajoutée en dur car absente du dataset image
D3E_INFO = {"bin": "D3E", "label": "Bac Électronique (D3E)", "color": "#808080"}

# ----------------------------------------------------------------------
# 2) Détection D3E par mots-clés (appliquée sur le nom du produit Jumia,
#    avant l'appel au modèle image -- voir predictor.py)
# ----------------------------------------------------------------------
D3E_KEYWORDS = [
    "smartphone", "telephone", "téléphone", "iphone", "samsung galaxy",
    "chargeur", "charger", "cable usb", "câble usb",
    "ecouteur", "écouteur", "casque audio", "airpods", "bluetooth",
    "batterie", "power bank", "powerbank",
    "mixeur", "blender", "robot cuisine", "electromenager", "électroménager",
    "montre connectee", "montre connectée", "smartwatch",
    "television", "télévision", "tv led",
    "ordinateur", "laptop", "pc portable", "souris", "clavier",
    "rasoir electrique", "rasoir électrique", "seche cheveux", "sèche-cheveux",
]


def detect_d3e(product_name: str) -> bool:
    """
    Retourne True si le nom du produit correspond à un article électronique/D3E.
    Comparaison insensible à la casse.
    """
    name = product_name.lower()
    return any(keyword in name for keyword in D3E_KEYWORDS)


def get_bin_for_class(class_name: str) -> dict:
    """
    Retourne le dict {bin, label, color} pour une classe brute du dataset.
    Lève une erreur explicite si la classe est inconnue (fail-fast, évite
    les bugs silencieux si le dataset ou le modèle change).
    """
    if class_name not in CLASS_TO_BIN:
        raise KeyError(
            f"Classe inconnue '{class_name}'. Classes valides : {list(CLASS_TO_BIN.keys())}"
        )
    return CLASS_TO_BIN[class_name]
