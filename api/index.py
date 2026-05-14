from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time

class handler(BaseHTTPRequestHandler):

    def obtener_precio(self, url):
        # 1. Configuramos el scraper (simulando Firefox en Windows)
        scraper = cloudscraper.create_scraper(
            delay=5, 
            browser={
                'browser': 'firefox',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        try:
            # 2. Headers para que Investing no detecte el bot
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
            
            # Espera aleatoria para mayor seguridad
            time.sleep(random.uniform(1.0, 2.5))
            
            res = scraper.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Intentamos encontrar el precio con los diferentes selectores que usa Investing
                tag = soup.find("div", {"data-test": "instrument-price-last"}) or \
                      soup.select_one('span[data-test="instrument-price-last"]') or \
                      soup.find("span", {"id": "last_last"})
                
                if tag:
                    texto_precio = tag.get_text(strip=True)
                    # MODIFICACIÓN: Filtramos el texto para dejar solo los dígitos
                    # Esto elimina automáticamente puntos, comas y símbolos de moneda
                    solo_digitos = "".join(filter(str.isdigit, texto_precio))
                    return solo_digitos
                
                return "Tag_No_Encontrado"
            
            return f"Error_{res.status_code}"
            
        except Exception as e:
            return "Error_Excepcion"

    def do_GET(self):
        # URL del Rodio en Investing
        url_rodio = "https://es.investing.com/commodities/rhodium-99.99-futures"

        # Obtenemos el valor limpio (solo números)
        valor_rodio = self.obtener_precio(url_rodio)

        # Preparamos la respuesta JSON
        datos = {
            "rodio": valor_rodio,
            "status": "online" if valor_rodio.isdigit() else "blocked"
        }

        # Enviamos las cabeceras
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # Para evitar problemas de CORS
        self.end_headers()
        
        # Escribimos el JSON de salida
        self.wfile.write(json.dumps(datos).encode('utf-8'))
