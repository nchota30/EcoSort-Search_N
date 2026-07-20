# ♻️ EcoSort-Search

Application web d'aide au tri sélectif basée sur le Deep Learning et le scraping en direct de Jumia.

## 🎯 Description

L'utilisateur saisit le nom d'un produit. L'application recherche ce produit sur Jumia,
l'utilisateur sélectionne un résultat, puis un modèle de Deep Learning analyse le produit
et affiche la consigne de tri correspondante (poubelle jaune, verte, bleue, D3E ou marron).

## 👥 Équipe

| Étudiant | Rôle |
| :--- | :--- |
| N'cho Esly Odon Junior | Repo GitHub, Application & Docker |
| KOUADIO POYARD SAMUEL-ELIE | Entraînement du modèle IA (Jalon 1) |
| AHINON Gbèlidji Stéphanas | Scraping Jumia |

## 🏗️ Structure du projet

```
ecosort-search/
├── app/                # Application web (Streamlit/Flask)
│   ├── main.py
│   ├── scraper/        # Module de scraping Jumia
│   └── model/          # Chargement et prédiction du modèle
├── training/           # Scripts d'entraînement du modèle CNN
├── models/             # Modèle entraîné (.h5)
├── data/               # Dataset Kaggle (non versionné)
├── docs/               # Documentation, rapport
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🚀 Installation et lancement

### En local (développement)

```bash
python -m venv .venv
source .venv/Scripts/activate   # Git Bash sous Windows
pip install -r requirements.txt
streamlit run app/main.py
```

### Avec Docker

```bash
docker build -t ecosort .
docker run -p 8501:8501 ecosort
```

ou

```bash
docker-compose up -d --build
```

## 🏷️ Catégories de tri

| Catégorie | Couleur | Matières |
| :--- | :--- | :--- |
| Poubelle JAUNE | 🟡 | plastic, metal, cardboard |
| Poubelle VERTE | 🟢 | glass |
| Poubelle BLEUE | 🔵 | paper |
| Bac D3E | 🎛️ | électronique (piles/batterie/prise) |
| Poubelle MARRON | ⚫ | trash |

## 🧠 Modèle IA

- Dataset : [Garbage Classification (Kaggle)](https://www.kaggle.com/code/muhammedabdulazeem/garbage-classification)
- Approche : Transfer Learning (MobileNetV2) / CNN custom
- Fichier modèle : `models/modele_eco_sort.h5`

## 🔀 Workflow Git

- Branche `main` protégée, aucun push direct
- Chaque fonctionnalité sur une branche dédiée
- Toute modification passe par une Pull Request relue par un autre membre

## 📅 Deadline

25/07/2026 - 23:59:59