from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time

class handler(BaseHTTPRequestHandler):

    def obtener_precio(self, scraper, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/'
        }
        
        try:
            # Bajamos el delay a 2 para que Vercel no nos corte la conexión
            res = scraper.get(url, headers=headers, timeout=10)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                # Tu lógica de búsqueda múltiple
                tag = soup.find("div", {"data-test": "instrument-price-last"}) or \
                      soup.select_one('span[data-test="instrument-price-last"]') or \
                      soup.find("span", {"id": "last_last"})
                
                if tag:
                    return tag.get_text(strip=True).replace(',', '')
                return "Tag_No_Encontrado"
            
            return f"Error_{res.status_code}"
            
        except Exception:
            return "Error_Excepcion"

    def do_GET(self):
        # Creamos un solo scraper para ambas peticiones (más eficiente)
        scraper = cloudscraper.create_scraper(browser={'browser': 'firefox', 'platform': 'windows', 'mobile': False})

        hierro_url = "https://www.investing.com/commodities/iron-ore-62-cfr-futures"
        carbon_url = "https://www.investing.com/commodities/coal-cme-futures"

        # Primera petición
        h_val = self.obtener_precio(scraper, hierro_url)
        
        # Pequeño respiro aleatorio entre peticiones
        time.sleep(random.uniform(0.5, 1.5))
        
        # Segunda petición
        c_val = self.obtener_precio(scraper, carbon_url)

        datos = {
            "hierro": h_val,
            "carbon": c_val,
            "status": "online" if "Error" not in h_val else "blocked"
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(datos).encode('utf-8'))