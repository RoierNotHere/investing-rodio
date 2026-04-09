from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
import time
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "https://es.investing.com/commodities/rhodium-99.99-futures"
        
        # 1. Metemos un delay random entre 1 y 5 segundos antes de empezar
        # Esto engaña a los sistemas que miden la velocidad de respuesta
        time.sleep(random.uniform(1.0, 5.0))
        
        # 2. Rotamos un poco el User-Agent también por si acaso
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]

        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.google.com/",
            "Cache-Control": "no-cache" # Le decimos que no queremos nada de cache
        }
        
        try:
            respuesta = requests.get(url, headers=headers, timeout=15)
            
            if respuesta.status_code == 200:
                soup = BeautifulSoup(respuesta.text, "html.parser")
                elemento = soup.find(attrs={"data-test": "instrument-price-last"})
                
                if elemento:
                    payload = {
                        "material": "Rodio",
                        "precio": elemento.text.strip(),
                        "status": "success",
                        "delay_aplicado": "random" 
                    }
                    status_code = 200
                else:
                    payload = {"error": "Selector no encontrado"}
                    status_code = 404
            else:
                payload = {"error": f"Bloqueo: {respuesta.status_code}"}
                status_code = respuesta.status_code
                
        except Exception as e:
            payload = {"error": str(e)}
            status_code = 500

        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return