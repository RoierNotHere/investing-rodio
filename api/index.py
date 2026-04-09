from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        
        # URL de Rodio en Investing
        url = "https://es.investing.com/commodities/rhodium-99.99-futures"
        
        try:
            # Investing es muy estricto, cloudscraper es clave aquí
            res = scraper.get(url, timeout=20)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Selector específico de Investing para el precio actual
                elemento = soup.find(attrs={"data-test": "instrument-price-last"})
                
                if elemento:
                    precio = elemento.text.strip()
                    payload = {
                        "material": "Rodio",
                        "precio": precio,
                        "moneda": "USD/OZ",
                        "fuente": "Investing.com",
                        "status": "success"
                    }
                    status_code = 200
                else:
                    payload = {"error": "No se encontró el precio (selector data-test)"}
                    status_code = 404
            else:
                payload = {"error": f"Error Investing: {res.status_code}"}
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