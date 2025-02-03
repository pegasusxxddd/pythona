import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que JavaScript en tu web acceda a la API

def obtener_datos_dni(dni):
    url = "https://eldni.com/pe/buscar-datos-por-dni"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": url,
        "Origin": "https://eldni.com",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    # Intentamos obtener la página principal para capturar el token CSRF
    try:
        session = requests.Session()
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        token_input = soup.find("input", {"name": "_token"})
        
        if not token_input or not token_input.get("value"):
            return {"error": "No se pudo obtener el token CSRF"}
        
        csrf_token = token_input["value"]
    except requests.exceptions.RequestException as e:
        return {"error": f"Error al obtener el token CSRF: {str(e)}"}

    # Datos a enviar con el token dinámico
    data = {
        "_token": csrf_token,
        "dni": dni,
    }

    # Enviar solicitud POST
    try:
        response = session.post(url, headers=headers, data=data)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        nombre_completo = soup.find("samp", {"class": "inline-block"})

        if nombre_completo:
            return {"nombre_completo": nombre_completo.text.strip()}
        else:
            return {"error": "No se encontraron datos para el DNI proporcionado"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error en la solicitud: {str(e)}"}

@app.route("/dni", methods=["GET"])
def obtener_dni():
    dni = request.args.get("dni")
    if not dni:
        return jsonify({"error": "DNI no proporcionado"}), 400

    resultado = obtener_datos_dni(dni)
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
