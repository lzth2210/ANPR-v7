# server.py
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)

# Variable compartida (thread-safe suficiente para este caso simple)
_latest_plate = {"plate": None, "timestamp": 0, "slot": None}

@app.route("/")
def index():
    # Página simple que hace polling cada 800ms
    html = """
    <!doctype html>
    <html lang="es">
        <head>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width,initial-scale=1"/>
            <title>ANPR Services - INNOVATE7</title>
            <style>
                :root{
                --blue:#1f5fbf;
                --blue-dark:#144a98;
                --bg:#eef1f6;
                --text:#0b2340;
                --border:#1f5fbf;
                --card:#ffffff;
                }
                *{box-sizing:border-box}
                body{
                font-family:Inter,Arial,Helvetica,sans-serif;
                background:var(--bg);
                color:var(--text);
                margin:0;
                min-height:100vh;
                display:flex;
                align-items:center;
                justify-content:center;
                }
                .header{
                position:fixed;
                top:0; left:0; right:0;
                background:var(--blue);
                color:#fff;
                height:64px;
                display:flex;
                align-items:center;
                justify-content:center;
                box-shadow:0 4px 18px rgba(0,0,0,0.15);
                }
                .header .title{
                font-weight:700;
                letter-spacing:.5px;
                }
                .card{
                background:var(--card);
                width:720px;
                max-width:92vw;
                border-radius:16px;
                box-shadow:0 12px 38px rgba(23,44,75,0.18);
                padding:32px 36px;
                margin-top:96px;
                text-align:center;
                border:1px solid rgba(31,95,191,0.15);
                }
                .welcome{
                font-size:2.6rem;
                font-weight:800;
                color:var(--blue-dark);
                margin:8px 0 14px;
                }
                .check{
                width:72px; height:72px;
                border-radius:50%;
                border:3px solid var(--blue);
                margin:0 auto 12px;
                display:flex; align-items:center; justify-content:center;
                color:var(--blue);
                font-size:38px; font-weight:800;
                line-height:0;
                }
                .dots{
                height:1px;
                border-top:2px dotted var(--blue);
                margin:18px 0 24px;
                opacity:.8;
                }
                .table{
                width:100%;
                border:2px solid var(--border);
                border-radius:8px;
                overflow:hidden;
                background:#f7f9fc;
                }
                .row{
                display:grid;
                grid-template-columns:180px 1fr;
                border-top:2px solid var(--border);
                }
                .row:first-child{border-top:none}
                .cell{
                padding:16px 18px;
                display:flex; align-items:center;
                font-weight:700;
                color:var(--blue-dark);
                }
                .cell.label{
                background:#e9f1ff;
                color:var(--blue-dark);
                text-transform:uppercase;
                letter-spacing:.8px;
                }
                .cell.value{
                background:#fff;
                font-weight:600;
                color:#0b2340;
                }
                .meta{
                margin-top:14px;
                font-size:.95rem;
                color:#576b88;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">ANPR Services - INNOVATE7</div>
            </div>

            <main class="card">
                <div class="welcome">¡Bienvenido!</div>
                <div class="check">✓</div>
                <div class="dots"></div>

                <div class="table" id="info-table">
                    <div class="row">
                        <div class="cell label">PLACA</div>
                        <div class="cell value" id="val-placa">---</div>
                    </div>
                    <div class="row">
                        <div class="cell label">SLOT</div>
                        <div class="cell value" id="val-slot">---</div>
                    </div>
                    <div class="row">
                        <div class="cell label">H. ENTRADA</div>
                        <div class="cell value" id="val-hora">---</div>
                    </div>
                </div>

                <div class="meta" id="meta">Esperando detecciones...</div>
            </main>

            <script>
                async function fetchLatest(){
                    try {
                        const res = await fetch('/latest');
                        if(!res.ok) return;
                        const j = await res.json();
                        const placa = j.plate || '---';
                        const slot = j.slot || '---';
                        const hora = j.timestamp ? new Date(j.timestamp*1000).toLocaleTimeString() : '---';

                        document.getElementById('val-placa').innerText = placa;
                        document.getElementById('val-slot').innerText = slot;
                        document.getElementById('val-hora').innerText = hora;

                        document.getElementById('meta').innerText = j.timestamp
                        ? `Última actualización: ${hora}`
                        : 'Esperando detecciones...';
                    } catch(e) {}
                }

                setInterval(fetchLatest, 800);
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
    slot = data.get("slot")
    if not plate:
        return jsonify({"success": False, "error": "no plate"}), 400
    # actualizar la variable compartida
    _latest_plate["plate"] = plate
    _latest_plate["slot"] = slot
    _latest_plate["timestamp"] = int(time.time())
    return jsonify({"success": True})

@app.route("/latest", methods=["GET"])
def latest():
    return jsonify({
        "plate": _latest_plate["plate"],
        "slot": _latest_plate["slot"],
        "timestamp": _latest_plate["timestamp"]
    })

if __name__ == "__main__":
    # Ejecuta en 0.0.0.0 si quieres acceder desde otra máquina (o Colab tunnel)
    app.run(host="0.0.0.0", port=5000, debug=False)
