"""
config.py
---------
Configuration centrale du pipeline d'entraînement EcoSort.
Toutes les valeurs modifiables (chemins, hyperparamètres) sont ici,
pour que train.py reste lisible et que l'entraînement soit reproductible.
"""

import os

# ----------------------------------------------------------------------
# Chemins
# ----------------------------------------------------------------------
# Racine du module (permet de lancer le script depuis n'importe où)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

# Où sauvegarder le modèle entraîné (livrable Jalon 1)
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "modele_eco_sort.h5")

# Où sauvegarder les artefacts d'entraînement (courbes, rapport, matrice de confusion)
OUTPUTS_DIR = os.path.join(BASE_DIR,"docs", "outputs")
HISTORY_PLOT_PATH = os.path.join(OUTPUTS_DIR, "training_history.png")
CONFUSION_MATRIX_PATH = os.path.join(OUTPUTS_DIR, "confusion_matrix.png")
CLASSIFICATION_REPORT_PATH = os.path.join(OUTPUTS_DIR, "classification_report.txt")
CLASS_INDICES_PATH = os.path.join(OUTPUTS_DIR, "class_indices.json")

# ----------------------------------------------------------------------
# Classes du dataset (ordre fixé une fois pour toutes -> reproductibilité)
# Ce sont les classes BRUTES du dataset Kaggle, pas les 5 poubelles finales.
# Le mapping vers les poubelles officielles se fait dans labels.py.
# ----------------------------------------------------------------------
CLASS_NAMES = ["cardboard", "glass", "metal", "paper", "plastic", "trash","shoes","clothes","battery","biological"]
NUM_CLASSES = len(CLASS_NAMES)

# ----------------------------------------------------------------------
# Hyperparamètres image / entraînement
# ----------------------------------------------------------------------
IMG_HEIGHT = 224
IMG_WIDTH = 224
IMG_SIZE = (IMG_HEIGHT, IMG_WIDTH)
BATCH_SIZE = 32

VALIDATION_SPLIT = 0.2   # 80% train / 20% validation
SEED = 42                # graine fixe -> mêmes splits à chaque run

EPOCHS_HEAD = 15         # entraînement de la tête (base gelée)
EPOCHS_FINE_TUNE = 10    # fine-tuning (dégel des dernières couches du backbone)
LEARNING_RATE_HEAD = 1e-3
LEARNING_RATE_FINE_TUNE = 1e-5

# Architecture : "mobilenetv2" (transfer learning, recommandé) ou "custom_cnn"
ARCHITECTURE = "mobilenetv2"

# Nombre de couches du backbone à dégeler lors du fine-tuning
# (uniquement utilisé si ARCHITECTURE == "mobilenetv2")
FINE_TUNE_AT_LAYER = 100
