from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time

class handler(BaseHTTPRequestHandler):

    def obtener_precio(self, url):
        # 1. Creamos el scraper con tu configuración de Firefox
        scraper = cloudscraper.create_scraper(
            delay=5, # Bajamos un poco el delay para evitar el timeout de Vercel
            browser={
                'browser': 'firefox',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        try:
            # 2. Tus Headers de navegador real
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            }
            
            # Espera aleatoria para no parecer bot
            time.sleep(random.uniform(1.0, 2.5))
            
            res = scraper.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Tu lógica de selectores múltiples
                tag = soup.find("div", {"data-test": "instrument-price-last"}) or \
                      soup.select_one('span[data-test="instrument-price-last"]') or \
                      soup.find("span", {"id": "last_last"})
                
                if tag:
                    # Quitamos comas como en tu ejemplo
                    return tag.get_text(strip=True).replace(',', '')
                return "Tag_No_Encontrado"
            
            return f"Error_{res.status_code}"
            
        except Exception as e:
            return f"Error_Excepcion"

    def do_GET(self):
        # URL específica del Rodio en Investing
        url_rodio = "https://es.investing.com/commodities/rhodium-99.99-futures"

        # Obtenemos el valor usando tu función
        valor_rodio = self.obtener_precio(url_rodio)

        # Formato de respuesta JSON
        datos = {
            "rodio": valor_rodio,
            "status": "online" if "Error" not in valor_rodio else "blocked"
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(datos).encode('utf-8'))