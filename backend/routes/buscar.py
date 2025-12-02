from flask import Blueprint, request, jsonify
from models import db, PlateRecord
import time

buscar_bp = Blueprint('buscar', __name__)

@buscar_bp.route('/buscar', methods=['GET'])
def buscar():
    html = """
    <html>
    <head>
        <title>Buscar Placa</title>
        <style>
            body {font-family: Arial; text-align: center; margin-top: 50px;}
            input {padding: 10px; width: 300px;}
            ul {list-style: none; padding: 0; margin: 0; width: 300px; margin: auto;}
            li {padding: 8px; border: 1px solid #ccc; cursor: pointer;}
            li:hover {background: #eee;}
        </style>
    </head>
    <body>
        <h2>Buscar Placa</h2>
        <input type="text" id="search" placeholder="Escribe la placa...">
        <ul id="suggestions"></ul>

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
