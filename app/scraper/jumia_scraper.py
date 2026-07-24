import re
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
       
        try:
            self.products = []
            for page in range(1, max_pages + 1):
                url = self._build_url(category, search_query, page)
                logger.info(f"Scraping page {page}: {url}")

                products_page = self._fetch_and_parse(url)
                if not products_page:
                    logger.info(f"Aucun produit trouvé page {page}. Arrêt.")
                    break

                self.products.extend(products_page)
                time.sleep(1)

            logger.info(f"Total de produits scrapés: {len(self.products)}")
            return self.products

        except Exception as e:
            logger.error(f"Erreur lors du scraping Jumia CI: {str(e)}")
            return []

    def _build_url(self, category: str = None, search_query: str = None,
                   page: int = 1) -> str:
        if search_query:
            return f"{self.base_url}/catalog/?q={search_query}&page={page}"
        elif category:
            return f"{self.base_url}/{category}?page={page}"
        else:
            return f"{self.base_url}/?page={page}"

    def _fetch_and_parse(self, url: str) -> List[Dict]:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            products = []

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
        try:
            name_elem = item.find('h2', class_='prd-name') or item.find('h3', class_='name')
            name = name_elem.text.strip() if name_elem else "N/A"

            price_elem = item.find('span', class_='prc') or item.find('div', class_='prc')
            price_text = price_elem.text.strip() if price_elem else "N/A"
            price = self._clean_price(price_text)

            link_elem = item.find('a', class_='core') or item.find('a')
            href = link_elem.get('href', '') if link_elem else ""
            url = href if href.startswith('http') else f"{self.base_url}{href}"

            image_url = None
            img = item.find('img')
            if img:
                image_url = img.get('data-src') or img.get('data-original') or img.get('src') or None
                if image_url and image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url and image_url.startswith('/'):
                    image_url = f"{self.base_url}{image_url}"

            rating_elem = item.find('div', class_='stars')
            rating = rating_elem.get('data-rating', 'N/A') if rating_elem else "N/A"

            seller_elem = item.find('span', class_='seller')
            seller = seller_elem.text.strip() if seller_elem else "N/A"

            product = {
                'name': name,
                'price': price,
                'price_text': price_text,
                'url': url,
                'image_url': image_url,
                'rating': rating,
                'seller': seller,
                'scraped_at': datetime.now().isoformat()
            }

            return product

        except Exception as e:
            logger.error(f"Erreur extraction produit: {str(e)}")
            return None

    def _clean_price(self, price_text: str) -> float:
        
        try:
            match = re.search(r'\d[\d\s,.\u00A0]*\d|\d', price_text)
            if not match:
                return 0.0
            digits_only = re.sub(r'[^\d]', '', match.group(0))
            return float(digits_only) if digits_only else 0.0
        except:
            return 0.0

    def save_to_json(self, filename: str = 'products.json') -> None:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, ensure_ascii=False, indent=2)
            logger.info(f"Produits sauvegardés dans {filename}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde: {str(e)}")

    def save_to_csv(self, filename: str = 'products.csv') -> None:
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
        if not self.products:
            return {'min': 0, 'max': 0, 'average': 0}

        prices = [p['price'] for p in self.products if p['price'] > 0]
        return {
            'min': min(prices) if prices else 0,
            'max': max(prices) if prices else 0,
            'average': sum(prices) / len(prices) if prices else 0
        }

    def get_top_products(self, search_query: str = None, max_pages: int = 1, top_n: int = 5) -> List[Dict]:
        """Scrape et retourne les `top_n` produits pour une requête sous le format demandé.

        Le classement est fait par note décroissante puis prix croissant.
        Retourne une liste d'objets avec les clés: nom, image_url, lien, prix
        """
        self.scrape_products(search_query=search_query, max_pages=max_pages)

        def _rating_val(p):
            try:
                return float(p.get('rating', 0))
            except:
                return 0.0

        sorted_products = sorted(self.products, key=lambda p: (-_rating_val(p), p.get('price', float('inf'))))

        top = sorted_products[:top_n]

        formatted = []
        for p in top:
            prix_str = p.get('price_text') or ''
            try:
                if p.get('price') and float(p.get('price')) > 0:
                    prix_str = f"{int(float(p.get('price')))} FCFA"
            except:
                pass

            formatted.append({
                'nom': p.get('name', ''),
                'image_url': p.get('image_url') or '',
                'lien': p.get('url', ''),
                'prix': prix_str
            })

        return formatted
import json


def rechercher_top5(produit: str, max_pages: int = 1) -> list:
    """Recherche un produit sur Jumia CI et retourne le top 5 formaté."""
    scraper = JumiaScraper()
    top5 = scraper.get_top_products(
        search_query=produit,
        max_pages=max_pages,
        top_n=5
    )
    return top5


def main():
    # On demande toujours le produit à l'utilisateur
    produit = input("Entrez le nom du produit à rechercher : ").strip()

    resultats = rechercher_top5(produit)

    # Affichage au format JSON demandé
    print(json.dumps(resultats, ensure_ascii=False, indent=4))
if __name__ == "__main__":
    main()
