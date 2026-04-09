from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Lista de User-Agents para engañar al firewall
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
        ]

        # Creamos el scraper con un agente aleatorio de la lista
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'custom_agent': random.choice(user_agents)
            }
        )
        
        url = "https://es.investing.com/commodities/rhodium-99.99-futures"
        
        try:
            # Añadimos un delay pequeño opcional si haces muchas peticiones
            res = scraper.get(url, timeout=20)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Selector de Investing
                elemento = soup.find(attrs={"data-test": "instrument-price-last"})
                
                if elemento:
                    payload = {
                        "material": "Rodio",
                        "precio": elemento.text.strip(),
                        "status": "success"
                    }
                    status_code = 200
                else:
                    payload = {"error": "No se encontro el selector"}
                    status_code = 404
            else:
                # Si sigue dando 403, devolvemos el error para saber
                payload = {"error": f"Bloqueo detectado: {res.status_code}"}
                status_code = res.status_code
                
        except Exception as e:
            payload = {"error": str(e)}
            status_code = 500

        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return