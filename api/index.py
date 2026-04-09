from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Usamos exactamente tu configuración ganadora
        url = "https://es.investing.com/commodities/rhodium-99.99-futures"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.google.com/"
        }
        
        try:
            # Petición simple con tus cabeceras
            respuesta = requests.get(url, headers=headers, timeout=10)
            
            if respuesta.status_code == 200:
                soup = BeautifulSoup(respuesta.text, "html.parser")
                # Tu selector exacto
                elemento = soup.find(attrs={"data-test": "instrument-price-last"})
                
                if elemento:
                    payload = {
                        "material": "Rodio",
                        "precio": elemento.text.strip(),
                        "fuente": "Investing.com",
                        "status": "success"
                    }
                    status_code = 200
                else:
                    payload = {"error": "Selector no encontrado en Investing"}
                    status_code = 404
            else:
                payload = {"error": f"Error Investing: {respuesta.status_code}"}
                status_code = respuesta.status_code
                
        except Exception as e:
            payload = {"error": str(e)}
            status_code = 500

        # Enviar respuesta JSON a Vercel
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return