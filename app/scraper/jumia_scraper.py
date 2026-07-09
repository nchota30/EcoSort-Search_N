import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JumiaScraper:
    """Web scraper pour les produits et prix Jumia Côte d'Ivoire"""

    def __init__(self):
        self.base_url = "https://www.jumia.ci"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.products = []

    def scrape_products(self, category: str = None, search_query: str = None,
                       max_pages: int = 1) -> List[Dict]:
        """
        Scrape les produits sur Jumia CI

        Args:
            category: Catégorie de produit (optionnel)
            search_query: Terme de recherche (optionnel)
            max_pages: Nombre maximum de pages à scraper

        Returns:
            Liste de dictionnaires de produits avec nom, prix et métadonnées
        """
        try:
            for page in range(1, max_pages + 1):
                url = self._build_url(category, search_query, page)
                logger.info(f"Scraping page {page}: {url}")

                products_page = self._fetch_and_parse(url)
                if not products_page:
                    logger.info(f"Aucun produit trouvé page {page}. Arrêt.")
                    break

                self.products.extend(products_page)
                time.sleep(1)  # Respecter le serveur

            logger.info(f"Total de produits scrapés: {len(self.products)}")
            return self.products

        except Exception as e:
            logger.error(f"Erreur lors du scraping Jumia CI: {str(e)}")
            return []

    def _build_url(self, category: str = None, search_query: str = None,
                   page: int = 1) -> str:
        """Construit l'URL selon les paramètres de recherche"""
        if search_query:
            return f"{self.base_url}/catalog/?q={search_query}&page={page}"
        elif category:
            return f"{self.base_url}/{category}?page={page}"
        else:
            return f"{self.base_url}/?page={page}"

    def _fetch_and_parse(self, url: str) -> List[Dict]:
        """Récupère l'URL et parse les données produits"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            products = []

            # Sélecteurs à ajuster selon la structure HTML réelle de jumia.ci
            product_items = soup.find_all('article', class_='prd')

            for item in product_items:
                product_data = self._extract_product_info(item)
                if product_data:
                    products.append(product_data)

            return products

        except requests.RequestException as e:
            logger.error(f"Erreur lors de la requête {url}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Erreur lors du parsing: {str(e)}")
            return []

    def _extract_product_info(self, item) -> Dict:
        """Extrait les infos produit d'un élément HTML"""
        try:
            # Nom du produit
            name_elem = item.find('h2', class_='prd-name') or item.find('h3', class_='name')
            name = name_elem.text.strip() if name_elem else "N/A"

            # Prix
            price_elem = item.find('span', class_='prc') or item.find('div', class_='prc')
            price_text = price_elem.text.strip() if price_elem else "N/A"
            price = self._clean_price(price_text)

            # URL produit
            link_elem = item.find('a', class_='core') or item.find('a')
            href = link_elem.get('href', '') if link_elem else ""
            url = href if href.startswith('http') else f"{self.base_url}{href}"

            # Note
            rating_elem = item.find('div', class_='stars')
            rating = rating_elem.get('data-rating', 'N/A') if rating_elem else "N/A"

            # Vendeur
            seller_elem = item.find('span', class_='seller')
            seller = seller_elem.text.strip() if seller_elem else "N/A"

            product = {
                'name': name,
                'price': price,
                'price_text': price_text,
                'url': url,
                'rating': rating,
                'seller': seller,
                'scraped_at': datetime.now().isoformat()
            }

            return product

        except Exception as e:
            logger.error(f"Erreur extraction produit: {str(e)}")
            return None

    def _clean_price(self, price_text: str) -> float:
        """Nettoie et convertit le texte de prix en float (Franc CFA)"""
        try:
            cleaned = price_text.replace('CFA', '').replace('F', '').replace(' ', '')
            cleaned = cleaned.replace(',', '.')
            numeric_part = ''.join(c for c in cleaned if c.isdigit() or c == '.')
            return float(numeric_part) if numeric_part else 0.0
        except:
            return 0.0

    def save_to_json(self, filename: str = 'products.json') -> None:
        """Sauvegarde les produits en JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, ensure_ascii=False, indent=2)
            logger.info(f"Produits sauvegardés dans {filename}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde: {str(e)}")

    def save_to_csv(self, filename: str = 'products.csv') -> None:
        """Sauvegarde les produits en CSV"""
        try:
            import csv
            if not self.products:
                logger.warning("Aucun produit à sauvegarder")
                return

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.products[0].keys())
                writer.writeheader()
                writer.writerows(self.products)
            logger.info(f"Produits sauvegardés dans {filename}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde CSV: {str(e)}")

    def get_price_range(self) -> Dict:
        """Retourne le prix min, max et moyen des produits scrapés"""
        if not self.products:
            return {'min': 0, 'max': 0, 'average': 0}

        prices = [p['price'] for p in self.products if p['price'] > 0]
        return {
            'min': min(prices) if prices else 0,
            'max': max(prices) if prices else 0,
            'average': sum(prices) / len(prices) if prices else 0
        }


