# server.py
from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import time
from models import db, PlateRecord

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plates.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.secret_key = 'your_secret_key_here'

with app.app_context():
    db.create_all()


@app.route("/update_plate", methods=["POST"])
def update_plate():
    data = request.get_json(force=True)
    plate = data.get("plate")
    slot = data.get("slot")

    if not plate:
        return jsonify({"success": False, "error": "no plate"}), 400

    # -----------------------
    # 1) ENTRADA -> registrar
    # -----------------------
    if slot == "entrada":

        last_record = PlateRecord.query.filter_by(plate=plate).order_by(PlateRecord.id.desc()).first()

        if not last_record:
            record = PlateRecord(
                plate=plate,
                slot="entrada",
                timestamp=int(time.time())
            )
            db.session.add(record)
            db.session.commit()
            return jsonify({"success": True}), 200
        
        if last_record.slot == "pagado":
            record = PlateRecord(
                plate=plate,
                slot="entrada",
                timestamp=int(time.time())
            )
            db.session.add(record)
            db.session.commit()
            return jsonify({"success": True, "info": "nueva entrada despues de pagar"}), 200
        
        if last_record.slot == "entrada":
            return jsonify({"success": False, "error": "duplicate"}), 200
        
        return jsonify({"success": False, "error": "already active"}), 200

    # -----------------------
    # 2) OTROS SLOTS -> actualizar
    # -----------------------
    last = PlateRecord.query.filter_by(plate=plate).order_by(PlateRecord.id.desc()).first()

    # Si NO existe registro previo → ignorar
    if not last:
        return jsonify({"success": False, "error": "no previous entry"}), 200

    # Si el último registro NO fue entrada → ignorar
    if last.slot != "entrada":
        return jsonify({"success": False, "error": "not from entrada"}), 200

    # Si el nuevo slot es igual al actual → ignorar (dup)
    if last.slot == slot:
        return jsonify({"success": False, "error": "same slot"}), 200

    # Registrar el nuevo slot pero conservar el timestamp de entrada
    new_record = PlateRecord(
        plate=plate,
        slot=slot,
        timestamp=last.timestamp   # se mantiene la hora de entrada
    )
    db.session.add(new_record)
    db.session.commit()

    return jsonify({"success": True, "info": "slot updated"}), 200


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
            if r.slot != "salida":
                html += f"<td><a href='/factura?plate={r.plate}'>Facturar</a></td></tr>"
            else:
                html += "<td>Ya facturado</td></tr>"
        html += "</table></body></html>"
        return html

@app.route("/buscar", methods=["GET"])
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


@app.route("/sugerencias", methods=["GET"])
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

@app.route("/factura", methods=["GET"])
def factura():
    plate = request.args.get("plate", None)

    if not plate:
        return "<h1 style='color:red;text-align:center;'>No plate provided</h1>"

    # Buscar la entrada original
    last = PlateRecord.query.filter_by(plate=plate).order_by(PlateRecord.id.desc()).first()
    if not last or last.slot == "pagado":
        return f"<h1 style='color:red;text-align:center;'>Esta placa ya fue pagada</h1>"

    entrada = PlateRecord.query.filter_by(plate=plate, slot="entrada").order_by(PlateRecord.id.asc()).first()
    ts_entrada = entrada.timestamp if entrada else int(time.time())

    # Registrar salida como "pagado"
    record = PlateRecord(
        plate=plate,
        slot="pagado",
        timestamp=ts_entrada
    )
    db.session.add(record)
    db.session.commit()

    # Calcular tiempo de permanencia
    tiempo_total = int(time.time()) - ts_entrada
    minutos = tiempo_total // 60

    ultimo = plate[-1]
    if ultimo.isdigit():
        tarifa = 1500
        tipo = "carro"
    else:
        tarifa = 1000
        tipo = "moto"

    valor_a_pagar = minutos * tarifa # Ejemplo: $0.05 por minuto

    html = f"""
    <html>
    <head>
        <title>Factura</title>
        <style>
            body {{font-family: Arial; text-align: center; margin-top: 50px;}}
            .box {{padding: 20px; border: 2px solid #333; display: inline-block; background: #f0f0f0;}}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Factura</h2>
            <p>Placa: <strong>{plate}</strong></p>
            <p>Tiempo total: {minutos} minutos</p>
            <p>Tipo de vehículo: <strong>{tipo}</strong></p>
            <p>Tarifa por minuto: <strong>${tarifa}</strong></p>
            <p>Valor a pagar: <strong>${valor_a_pagar}</strong></p>
            <form action="/pago_exitoso" method="get">
                <button type="submit">Pagar ahora</button>
            </form>
        </div>
    </body>
    </html>
    """
    return html

@app.route("/pago_exitoso", methods=["GET"])
def pago_exitoso():
    html = """
    <html>
    <head>
        <title>Gracias</title>
        <style>
            body {font-family: Arial; text-align: center; margin-top: 100px;}
            .box {padding: 20px; border: 2px solid #333; display: inline-block; background: #d4edda;}
            h2 {color: green;}
        </style>
        <script>
            // Redirigir a /buscar después de 5 segundos
            setTimeout(function(){
                window.location.href = "/buscar";
            }, 5000);
        </script>
    </head>
    <body>
        <div class="box">
            <h2>¡Gracias por su pago!</h2>
            <p>Será redirigido en unos segundos...</p>
        </div>
    </body>
    </html>
    """
    return html

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Login muy sencillo (hardcodeado)
        if username == "liz" and password == "1234":
            session["user"] = "admin"
            return redirect(url_for("admin"))
        else:
            return "<h3 style='color:red;text-align:center;'>Credenciales inválidas</h3>"

    # Formulario de login
    return """
    <html>
    <head><title>Login</title></head>
    <body style="text-align:center; margin-top:50px;">
        <h2>Login Administrador</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Usuario"><br><br>
            <input type="password" name="password" placeholder="Contraseña"><br><br>
            <button type="submit">Ingresar</button>
        </form>
    </body>
    </html>
    """

@app.route("/admin")
def admin():

    # Aquí puedes reutilizar la lógica de /tabla
        subquery = db.session.query(
            PlateRecord.plate,
            db.func.max(PlateRecord.id).label("max_id")
        ).group_by(PlateRecord.plate).subquery()

        records = db.session.query(PlateRecord).join(
            subquery, PlateRecord.id == subquery.c.max_id
        ).all()

        html = """
        <html>
        <head>
            <title>Vista Administrador</title>
            <style>
                table {border-collapse: collapse; width: 80%; margin: 20px auto;}
                th, td {border: 1px solid #333; padding: 8px; text-align: center;}
                th {background-color: #1f5fbf; color: white;}
            </style>
        </head>
        <body>
            <h2 style="text-align:center;">Panel de Administrador</h2>
            <h3 style="text-align:center;">Tabla de Placas</h3>
            <table>
                <tr><th>ID</th><th>Placa</th><th>Slot</th><th>Hora</th></tr>
        """
        for r in records:
            hora = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r.timestamp))
            html += f"<tr><td>{r.id}</td><td>{r.plate}</td><td>{r.slot}</td><td>{hora}</td></tr>"
        html += "</table>"

        # Transmisión en vivo (ejemplo con iframe de cámara IP o video)
        html += """
            <h3 style="text-align:center;">Transmisión en vivo</h3>
            <div style="text-align:center;">
                <iframe src="http://tu-streaming-url" width="640" height="360" frameborder="0" allowfullscreen></iframe>
            </div>
        </body>
        </html>
        """
        return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)