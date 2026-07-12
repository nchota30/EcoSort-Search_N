
## Utilisation du model
```python
from app.model.predictor import EcoSortPredictor

predictor = EcoSortPredictor()  #faire ça une seul fois
result = predictor.predict_from_bytes(image_bytes, product_name="")

#{'bin': 'D3E', 'label': 'Bac Électronique (D3E)', 'color': '#808080',
# 'confidence': 0.9999, 'raw_class': 'battery'}

#Le resultat sort sous forme de dictionnaire
#Tu peux utiliser aussi le product_name pour obtenir une prediction , c'est par a la consigne sur le D3E
```

## Fichiers
| Fichier | Rôle |
| `config.py` (racine) | Chemins + hyperparamètres, partagé par tout le projet |
| `training/data_loader.py` | Chargement et augmentation des données |
| `training/model.py` | Architectures (MobileNetV2 / CNN custom) |
| `training/train.py` | Le script d'entraînement |
| `app/model/labels.py` | Mapping classes → 5 poubelles officielles et détection D3E |
| `app/model/predictor.py` | Classe `EcoSortPredictor`, à importer dans `main.py` |
