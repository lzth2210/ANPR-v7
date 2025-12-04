from flask import Blueprint, request, jsonify
from models import db, PlateRecord
import time

buscar_bp = Blueprint('buscar', __name__)

@buscar_bp.route('/buscar', methods=['GET'])
def buscar():
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8" />
        <title>Buscar Placa</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI', Roboto, sans-serif;
                background: #f3f4f6;
                color: #111827;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                min-height: 100vh;
            }
            .header {
                background-color: #3b82f6;
                color: white;
                width: 100%;
                padding: 20px 0;
                font-size: 24px;
                font-weight: bold;
                text-align: center;
            }
            .content {
                margin-top: 60px;
                text-align: center;
            }
            .content h2 {
                font-size: 32px;
                margin-bottom: 12px;
                color: #235284;
            }
            .content p {
                font-size: 18px;
                color: #374151;
                margin-bottom: 24px;
            }
            input[type="text"] {
                padding: 12px;
                width: 320px;
                font-size: 16px;
                border: 2px solid #3b82f6;
                border-radius: 8px;
                outline: none;
            }
            ul {
                list-style: none;
                padding: 0;
                margin-top: 20px;
                width: 320px;
            }
            li {
                padding: 10px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                margin-bottom: 8px;
                background: white;
                cursor: pointer;
                transition: background 0.2s ease;
            }
            li:hover {
                background: #e0f2fe;
            }
        </style>
    </head>
    <body>
        <div class="header">BUSQUEDA</div>
        <div class="content">
            <h2>¡Bienvenido!</h2>
            <p>Busque su placa a continuación:</p>
            <input type="text" id="search" placeholder="EJ: ABC123" />
            <ul id="suggestions"></ul>
        </div>

        <script>
            const input = document.getElementById("search");
            const suggestions = document.getElementById("suggestions");

            input.addEventListener("input", function() {
                fetch("/sugerencias?query=" + input.value)
                    .then(res => res.json())
                    .then(data => {
                        suggestions.innerHTML = "";
                        data.forEach(plate => {
                            const li = document.createElement("li");
                            li.textContent = plate;
                            li.onclick = () => {
                                window.location.href = "/factura?plate=" + plate;
                            };
                            suggestions.appendChild(li);
                        });
                    });
            });
        </script>
    </body>
    </html>
    """
    return html

@buscar_bp.route('/sugerencias', methods=['GET'])
def sugerencias():
    query = request.args.get("query", "").upper()
    if not query:
        return jsonify([])

    subquery = db.session.query(
        PlateRecord.plate,
        db.func.max(PlateRecord.id).label("max_id")
    ).group_by(PlateRecord.plate).subquery()

    results = db.session.query(PlateRecord).join(
        subquery, PlateRecord.id == subquery.c.max_id
    ).filter(PlateRecord.plate.like(f"{query}%"), PlateRecord.slot != "pagado").all()

    return jsonify([r.plate for r in results])
