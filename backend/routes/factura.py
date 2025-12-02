from flask import Blueprint, request, jsonify
from models import db, PlateRecord
import time

factura_bp = Blueprint('factura', __name__)

@factura_bp.route('/factura', methods=['POST'])
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

@factura_bp.route('/pago_exitoso', methods=['GET'])
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
