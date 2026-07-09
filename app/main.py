"""
Point d'entrée principal de l'application EcoSort
Scrape Jumia et analyse les produits avec le modèle ML
"""

import logging
from scraper import JumiaScraper
from data_loader import DataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Fonction principale"""
    logger.info("=== EcoSort-Search ===\n")
    
    # 1. Vérifier les données existantes
    logger.info("📊 Vérification des données disponibles...")
    available_files = DataLoader.list_available_files()
    
    if available_files['json'] or available_files['csv']:
        logger.info(f"✓ Fichiers JSON trouvés: {available_files['json']}")
        logger.info(f"✓ Fichiers CSV trouvés: {available_files['csv']}")
        
        total_products = DataLoader.get_total_products()
        logger.info(f"✓ Total de produits existants: {total_products}\n")
        
        # Charger et afficher un aperçu
        if available_files['json']:
            products = DataLoader.load_from_json(available_files['json'][0])
            if products:
                logger.info("Aperçu des produits:")
                for product in products[:3]:
                    logger.info(f"  - {product.get('name', 'N/A')} | {product.get('price_text', 'N/A')}")
    else:
        logger.warning("⚠️ Aucune donnée existante trouvée")
        logger.info("📥 Lancement du scraping Jumia...\n")
        
        # 2. Scraper de nouvelles données
        scraper = JumiaScraper()
        products = scraper.scrape_products(
            search_query="electronique",
            max_pages=2
        )
        
        if products:
            logger.info(f"✓ {len(products)} produits scrapés\n")
            # Afficher les premiers résultats
            for i, product in enumerate(products[:3], 1):
                logger.info(f"{i}. {product['name']}")
                logger.info(f"   Prix: {product['price_text']}")
                logger.info(f"   Note: {product['rating']}\n")
            
            # 3. Sauvegarder les données
            scraper.save_to_json('products.json')
            scraper.save_to_csv('products.csv')
        else:
            logger.error("✗ Aucun produit trouvé pendant le scraping")


if __name__ == "__main__":
    main()
