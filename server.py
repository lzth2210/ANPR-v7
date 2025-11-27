# server.py
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)

# Variable compartida (thread-safe suficiente para este caso simple)
_latest_plate = {"value": None, "timestamp": 0}

@app.route("/")
def index():
    # Página simple que hace polling cada 800ms
    html = """
    <!doctype html>
    <html lang="es">
    <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width,initial-scale=1"/>
        <title>ANPR - Resultados</title>
        <style>
            body{font-family:Inter,Arial,sans-serif;background:#0b0b0f;color:#e6e6e6;display:flex;
            align-items:center;justify-content:center;height:100vh;margin:0}
            .card{background:#111;padding:28px;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,0.6);
            text-align:center;min-width:320px}
            #placa{font-size:3.2rem;letter-spacing:6px;padding:14px 22px;border-radius:8px;border:2px solid #0f0;
            display:inline-block;background:#0b0b0b}
            .meta{margin-top:10px;font-size:0.9rem;color:#aab}
        </style>
    </head>
    <body>
        <div class="card">
            <div id="placa">---</div>
            <div class="meta" id="meta">Esperando detecciones...</div>
        </div>

        <script>
            async function fetchLatest(){
                try {
                    const res = await fetch('/latest');
                    if(!res.ok) return;
                    const j = await res.json();
                    const placa = j.plate || '---';
                    document.getElementById('placa').innerText = placa;
                    const t = j.timestamp ? new Date(j.timestamp*1000).toLocaleTimeString() : '';
                    document.getElementById('meta').innerText = t ? `Última: ${t}` : 'Esperando detecciones...';
                } catch(e){
                    // console.log(e);
                }
            }

            // Polling cada 800 ms (ajusta si quieres menos requests)
            setInterval(fetchLatest, 800);
            // petición inicial
            fetchLatest();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/update_plate", methods=["POST"])
def update_plate():
    data = request.get_json(force=True)
    plate = data.get("plate")
    if not plate:
        return jsonify({"success": False, "error": "no plate"}), 400
    # actualizar la variable compartida
    _latest_plate["value"] = plate
    _latest_plate["timestamp"] = int(time.time())
    return jsonify({"success": True})

@app.route("/latest", methods=["GET"])
def latest():
    return jsonify({
        "plate": _latest_plate["value"],
        "timestamp": _latest_plate["timestamp"]
    })

if __name__ == "__main__":
    # Ejecuta en 0.0.0.0 si quieres acceder desde otra máquina (o Colab tunnel)
    app.run(host="0.0.0.0", port=5000, debug=False)
