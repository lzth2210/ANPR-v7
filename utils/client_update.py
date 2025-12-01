# client_update.py (pequeña función que puedes importar en tu main)
import requests
import json

SERVER_URL = "http://127.0.0.1:5000"  # cambia si el servidor está en otra máquina o en Colab

def send_plate_to_web(plate: str, slot: str):
    try:
        payload = {"plate": plate, "slot": slot}
        r = requests.post(f"{SERVER_URL}/update_plate", json=payload, timeout=2)
        # opcional: chequear r.status_code o r.json()
        return r.ok
    except Exception as e:
        # loguea pero no rompas el pipeline
        print("Error enviando plate -> web:", e)
        return False
