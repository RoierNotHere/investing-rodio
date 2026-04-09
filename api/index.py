from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import time
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Delay aleatorio inicial para no parecer un bot
        time.sleep(random.uniform(1.5, 4.0))

        # 2. Configurar el scraper
        # Usamos cloudscraper para saltar protecciones de JS
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )

        url = "https://es.investing.com/commodities/rhodium-99.99-futures"
        
        # 3. Headers adicionales (los que te funcionaron con requests)
        headers = {
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.google.com/",
            "Cache-Control": "no-cache"
        }

        try:
            # Hacemos la petición
            res = scraper.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                # Selector de precio
                elemento = soup.find(attrs={"data-test": "instrument-price-last"})
                
                if elemento:
                    payload = {
                        "material": "Rodio",
                        "precio": elemento.text.strip(),
                        "status": "success",
                        "method": "cloudscraper"
                    }
                    status_code = 200
                else:
                    payload = {"error": "No se encontro el selector de precio"}
                    status_code = 404
            else:
                payload = {"error": f"Error de Investing: {res.status_code}"}
                status_code = res.status_code
                
        except Exception as e:
            payload = {"error": str(e)}
            status_code = 500

        # Respuesta JSON
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return