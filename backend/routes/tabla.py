from flask import Blueprint, request, jsonify
from models import db, PlateRecord
import time

tabla_bp = Blueprint('tabla', __name__)

@tabla_bp.route('/tabla', methods=['GET'])
def tabla():

    # Obtener el último estado por placa
        subquery = db.session.query(
            PlateRecord.plate,
            db.func.max(PlateRecord.id).label("max_id")
        ).group_by(PlateRecord.plate).subquery()

        records = db.session.query(PlateRecord).join(
            subquery,
            PlateRecord.id == subquery.c.max_id
        ).all()

        html = """
        <html>
        <head>
            <title>Registros de Placas</title>
            <style>
                table {border-collapse: collapse; width: 80%; margin: 20px auto;}
                th, td {border: 1px solid #333; padding: 8px; text-align: center;}
                th {background-color: #1f5fbf; color: white;}
            </style>
            <script>
                // Refrescar la página cada 3 segundos
                setInterval(function(){
                    window.location.reload();
                }, 3000);
            </script>
        </head>
        <body>
            <h2 style="text-align:center;">Último estado de cada placa</h2>
            <table>
                <tr><th>ID</th><th>Placa</th><th>Slot</th><th>Hora Entrada</th><th>Acción</th></tr>
        """
        for r in records:
            hora = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r.timestamp))
            html += f"<tr><td>{r.id}</td><td>{r.plate}</td><td>{r.slot}</td><td>{hora}</td>"
            if r.slot != "pagado":
                html += f"<td><a href='/factura?plate={r.plate}'>Facturar</a></td></tr>"
            else:
                html += "<td>Ya facturado</td></tr>"
        html += "</table></body></html>"
        return html

@tabla_bp.route('/latest', methods=['GET'])
def latest():
    record = PlateRecord.query.order_by(PlateRecord.id.desc()).first()
    if not record:
        return jsonify({
            "plate": None,
            "slot": None,
            "timestamp": 0
        })
    return jsonify({
        "plate": record.plate,
        "slot": record.slot,
        "timestamp": record.timestamp
    })
