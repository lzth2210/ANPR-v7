# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from models import db, PlateRecord

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plates.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/update_plate", methods=["POST"])
def update_plate():
    data = request.get_json(force=True)
    plate = data.get("plate")
    slot = data.get("slot")

    if not plate:
        return jsonify({"success": False, "error": "no plate"}), 400

    # 🔹 Lógica: solo aceptar si el slot es "entrada"
    if slot == "entrada":
        # Evitar duplicado consecutivo en entrada
        last_record = PlateRecord.query.filter_by(
            plate=plate, slot="entrada"
        ).order_by(PlateRecord.id.desc()).first()

        if last_record:
            return jsonify({"success": False, "error": "duplicate"}), 200

        record = PlateRecord(
            plate=plate,
            slot="entrada",
            timestamp=int(time.time())
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({"success": True})

    last = PlateRecord.query.filter_by(plate=plate).order_by(PlateRecord.id.desc()).first()

    # Si NO existe registro previo → ignorar
    if not last:
        return jsonify({"success": False, "error": "no previous entry"}), 200

    # Si el último registro NO fue entrada → ignorar
    if last.slot != "entrada":
        return jsonify({"success": False, "error": "not from entrada"}), 200

    # Si el nuevo slot es igual al actual → ignorar
    if last.slot == slot:
        return jsonify({"success": False, "error": "same slot"}), 200

    # Registrar el nuevo slot
    new_record = PlateRecord(
        plate=plate,
        slot=slot,
        timestamp=int(time.time())
    )
    db.session.add(new_record)
    db.session.commit()

    return jsonify({"success": True, "info": "slot updated"})


@app.route("/latest", methods=["GET"])
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


@app.route("/tabla", methods=["GET"])
def tabla():
    # Obtener el último estado por placa
    subquery = db.session.query(
        PlateRecord.plate,
        db.func.max(PlateRecord.timestamp).label("max_ts")
    ).group_by(PlateRecord.plate).subquery()

    records = db.session.query(PlateRecord).join(
        subquery,
        (PlateRecord.plate == subquery.c.plate) &
        (PlateRecord.timestamp == subquery.c.max_ts)
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
            <tr><th>ID</th><th>Placa</th><th>Slot</th><th>Hora</th></tr>
    """
    for r in records:
        hora = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r.timestamp))
        html += f"<tr><td>{r.id}</td><td>{r.plate}</td><td>{r.slot}</td><td>{hora}</td></tr>"
    html += "</table></body></html>"
    return html


if __name__ == "__main__":
    # Ejecuta en 0.0.0.0 si quieres acceder desde otra máquina (o Colab tunnel)
    app.run(host="0.0.0.0", port=5000, debug=False)