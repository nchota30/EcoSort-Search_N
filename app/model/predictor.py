
import io
import json
import os

import numpy as np
import tensorflow as tf
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import config
from labels import get_bin_for_class, detect_d3e, D3E_INFO


class EcoSortPredictor:


    def __init__(self, model_path: str = None, class_indices_path: str = None):
        self.model_path = model_path or config.MODEL_PATH
        self.class_indices_path = class_indices_path or config.CLASS_INDICES_PATH

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Modèle introuvable : '{self.model_path}'. "
                "Lance d'abord train.py pour générer le fichier .h5."
            )

        self.model = tf.keras.models.load_model(self.model_path)
        self.class_names = self._load_class_names()

    def _load_class_names(self):

        if os.path.exists(self.class_indices_path):
            with open(self.class_indices_path) as f:
                return json.load(f)

        return sorted(config.CLASS_NAMES)

    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        image = image.convert("RGB").resize(config.IMG_SIZE)
        array = tf.keras.utils.img_to_array(image)
        array = np.expand_dims(array, axis=0)  # batch de taille 1
        return array

    def _predict_array(self, array: np.ndarray) -> dict:
        predictions = self.model.predict(array, verbose=0)[0]
        best_idx = int(np.argmax(predictions))
        confidence = float(predictions[best_idx])
        raw_class = self.class_names[best_idx]

        bin_info = get_bin_for_class(raw_class)
        return {
            "bin": bin_info["bin"],
            "label": bin_info["label"],
            "color": bin_info["color"],
            "confidence": round(confidence, 4),
            "raw_class": raw_class,
        }

    def predict(self, image: Image.Image, product_name: str = "") -> dict:
        """
        Point d'entrée principal.
        """
        if product_name and detect_d3e(product_name):
            return {
                "bin": D3E_INFO["bin"],
                "label": D3E_INFO["label"],
                "color": D3E_INFO["color"],
                "confidence": None,   
                "raw_class": None,
            }

        array = self._preprocess_image(image)
        return self._predict_array(array)

    def predict_from_path(self, image_path: str, product_name: str = "") -> dict:
        image = Image.open(image_path)
        return self.predict(image, product_name=product_name)

    def predict_from_bytes(self, image_bytes: bytes, product_name: str = "") -> dict:
        image = Image.open(io.BytesIO(image_bytes))
        return self.predict(image, product_name=product_name)


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print("Usage : python predictor.py <chemin_image> [nom_produit]")
        sys.exit(1)

    img_path = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else ""

    predictor = EcoSortPredictor()
    result = predictor.predict_from_path(img_path, product_name=name)
    print(result)
