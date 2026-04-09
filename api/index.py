from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time

class handler(BaseHTTPRequestHandler):

    def obtener_precio_rodio(self, url):
        # Configuramos el scraper con el motor de Firefox como pediste
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'firefox',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        try:
            # Headers realistas de navegación
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Referer': 'https://www.google.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site'
            }
            
            # Delay aleatorio para evitar el 403 por repetición
            time.sleep(random.uniform(1.0, 3.0))
            
            res = scraper.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Tu lógica de selectores múltiples (muy efectiva)
                tag = soup.find("div", {"data-test": "instrument-price-last"}) or \
                      soup.select_one('span[data-test="instrument-price-last"]') or \
                      soup.find("span", {"id": "last_last"})
                
                if tag:
                    # Limpiamos comas para que sea un número puro si quieres procesarlo
                    return tag.get_text(strip=True).replace(',', '')
                return "Tag_No_Encontrado"
            
            return f"Error_{res.status_code}"
            
        except Exception as e:
            return "Error_Excepcion"

    def do_GET(self):
        url_rodio = "https://es.investing.com/commodities/rhodium-99.99-futures"
        
        resultado = self.obtener_precio_rodio(url_rodio)

        # Estructura de respuesta limpia
        datos = {
            "material": "Rodio",
            "precio": resultado,
            "status": "online" if "Error" not in resultado else "blocked"
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(datos).encode('utf-8'))