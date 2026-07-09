import json
import csv
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Gestionnaire pour charger les données scrapées"""

    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

    @staticmethod
    def load_from_json(filename: str = 'products.json') -> List[Dict]:
        """Charge les produits depuis un fichier JSON"""
        filepath = os.path.join(DataLoader.DATA_DIR, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"Fichier JSON non trouvé: {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✓ Chargé {len(data)} produits depuis {filename}")
                return data
        except Exception as e:
            logger.error(f"Erreur chargement JSON: {str(e)}")
            return []

    @staticmethod
    def load_from_csv(filename: str = 'products.csv') -> List[Dict]:
        """Charge les produits depuis un fichier CSV"""
        filepath = os.path.join(DataLoader.DATA_DIR, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"Fichier CSV non trouvé: {filepath}")
            return []
        
        try:
            products = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                products = list(reader)
            logger.info(f"✓ Chargé {len(products)} produits depuis {filename}")
            return products
        except Exception as e:
            logger.error(f"Erreur chargement CSV: {str(e)}")
            return []

    @staticmethod
    def list_available_files() -> Dict[str, List[str]]:
        """Liste tous les fichiers de données disponibles"""
        json_files = []
        csv_files = []
        
        if os.path.exists(DataLoader.DATA_DIR):
            for file in os.listdir(DataLoader.DATA_DIR):
                if file.endswith('.json'):
                    json_files.append(file)
                elif file.endswith('.csv'):
                    csv_files.append(file)
        
        return {
            'json': json_files,
            'csv': csv_files
        }

    @staticmethod
    def get_total_products() -> int:
        """Retourne le nombre total de produits dans tous les fichiers"""
        available = DataLoader.list_available_files()
        total = 0
        
        for json_file in available['json']:
            products = DataLoader.load_from_json(json_file)
            total += len(products)
        
        return total
