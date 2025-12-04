from flask import Blueprint, request, jsonify
from models import db, PlateRecord, ser
import time

factura_bp = Blueprint('factura', __name__)

@factura_bp.route('/factura', methods=['GET', 'POST'])
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

    # Registrar pago como "pagado"
    record = PlateRecord(
        plate=plate,
        slot="pagado",
        timestamp=ts_entrada
    )
    db.session.add(record)
    db.session.commit()

    # Controlar hardware: abrir barrera y apagar LED del slot
    ser.write(b'V')  # Abrir barrera
    time.sleep(4)
    ser.write(b'R')  # Cerrar barrera

    # Buscar en qué slot estaba el vehículo antes de pagar
    slot_record = PlateRecord.query.filter_by(plate=plate).filter(
        PlateRecord.slot.like('slot%')
    ).order_by(PlateRecord.id.desc()).first()

    if slot_record and slot_record.slot.startswith("slot"):
        slot_number = slot_record.slot[-1]  # ej: "slot3" → "3"
        command_map = {
            "1": b'G',
            "2": b'H',
            "3": b'I',
            "4": b'J',
            "5": b'K',
            "6": b'L'
        }
        ser.write(command_map[slot_number])  # Apagar LED del slot

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
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8" />
            <title>Factura</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style>
                :root {{
                    --bg: #0f172a;
                    --card: #111827;
                    --text: #e5e7eb;
                    --muted: #9ca3af;
                    --accent: #3b82f6;
                    --accent-hover: #2563eb;
                    --success: #22c55e;
                    --border: #1f2937;
                }}
                * {{ box-sizing: border-box; }}
                body {{
                    margin: 0;
                    font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
                    background: radial-gradient(1200px circle at 20% 10%, #1e293b, var(--bg));
                    color: var(--text);
                    display: grid;
                    place-items: center;
                    min-height: 100vh;
                    padding: 24px;
                }}
                .container {{
                    width: 100%;
                    max-width: 680px;
                }}
                .card {{
                    background: linear-gradient(180deg, rgba(31,41,55,.8), rgba(17,24,39,.9));
                    border: 1px solid var(--border);
                    border-radius: 16px;
                    box-shadow: 0 20px 50px rgba(0,0,0,.35);
                    overflow: hidden;
                }}
                .header {{
                    padding: 24px 24px 8px;
                    border-bottom: 1px solid var(--border);
                }}
                .title {{
                    margin: 0;
                    font-size: 24px;
                    letter-spacing: .5px;
                }}
                .subtitle {{
                    margin: 8px 0 0;
                    color: var(--success);
                    font-weight: 600;
                    letter-spacing: .3px;
                }}
                .content {{
                    padding: 24px;
                }}
                .table {{
                    width: 100%;
                    border-collapse: collapse;
                    background: rgba(255,255,255,.02);
                    border: 1px solid var(--border);
                    border-radius: 12px;
                    overflow: hidden;
                }}
                .row {{
                    display: grid;
                    grid-template-columns: 220px 1fr;
                    gap: 16px;
                    padding: 14px 16px;
                    align-items: center;
                    border-bottom: 1px solid var(--border);
                }}
                .row:last-child {{
                    border-bottom: none;
                }}
                .label {{
                    color: var(--muted);
                    font-weight: 600;
                    text-transform: uppercase;
                    font-size: 12px;
                    letter-spacing: .8px;
                }}
                .value {{
                    font-weight: 600;
                    font-size: 16px;
                    color: var(--text);
                }}
                .footer {{
                    padding: 20px 24px 24px;
                    display: flex;
                    justify-content: flex-end;
                    gap: 12px;
                }}
                .btn {{
                    appearance: none;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 20px;
                    font-weight: 700;
                    letter-spacing: .4px;
                    cursor: pointer;
                    transition: transform .05s ease, background .2s ease, box-shadow .2s ease;
                }}
                .btn:active {{
                    transform: translateY(1px);
                }}
                .btn-pay {{
                    background: var(--accent);
                    color: white;
                    box-shadow: 0 10px 25px rgba(59,130,246,.35);
                }}
                .btn-pay:hover {{
                    background: var(--accent-hover);
                }}
                .note {{
                    margin-top: 12px;
                    font-size: 12px;
                    color: var(--muted);
                    text-align: right;
                }}
                @media (max-width: 520px) {{
                    .row {{
                        grid-template-columns: 1fr;
                        gap: 6px;
                    }}
                    .footer {{
                        justify-content: stretch;
                    }}
                    .btn {{
                        width: 100%;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card" role="region" aria-labelledby="factura-title">
                    <div class="header">
                        <h1 id="factura-title" class="title">FACTURA</h1>
                        <p class="subtitle">¡GRACIAS! Su factura está lista</p>
                    </div>

                    <div class="content">
                        <div class="table" role="table" aria-label="Detalles de facturación">
                            <div class="row" role="row">
                                <div class="label" role="cell">PLACA</div>
                                <div class="value" role="cell">{plate}</div>
                            </div>
                            <div class="row" role="row">
                                <div class="label" role="cell">TIPO DE VEHÍCULO</div>
                                <div class="value" role="cell">{tipo}</div>
                            </div>
                            <div class="row" role="row">
                                <div class="label" role="cell">TARIFA DE VEHÍCULO</div>
                                <div class="value" role="cell">$ {tarifa} / minuto</div>
                            </div>
                            <div class="row" role="row">
                                <div class="label" role="cell">TIEMPO TOTAL</div>
                                <div class="value" role="cell">{minutos} minutos</div>
                            </div>
                            <div class="row" role="row">
                                <div class="label" role="cell">VALOR A PAGAR</div>
                                <div class="value" role="cell">$ {valor_a_pagar}</div>
                            </div>
                        </div>

                        <p class="note">Revise los datos antes de continuar con el pago.</p>
                    </div>

                    <div class="footer">
                        <form action="/pago_exitoso" method="get">
                            <input type="hidden" name="plate" value="{plate}" />
                            <input type="hidden" name="tipo" value="{tipo}" />
                            <input type="hidden" name="minutos" value="{minutos}" />
                            <input type="hidden" name="tarifa" value="{tarifa}" />
                            <input type="hidden" name="valor" value="{valor_a_pagar}" />
                            <button type="submit" class="btn btn-pay" aria-label="Pagar factura">PAGAR</button>
                        </form>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    return html

@factura_bp.route('/pago_exitoso', methods=['GET'])
def pago_exitoso():
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8" />
        <title>Gracias</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta http-equiv="refresh" content="5; url=/buscar" />
        <style>
            body {{
                margin: 0;
                font-family: 'Segoe UI', Roboto, sans-serif;
                background: #f3f4f6;
                color: #111827;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                text-align: center;
            }}
            .header {{
                position: absolute;
                top: 0;
                background-color: #3b82f6;
                color: white;
                width: 100%;
                padding: 20px 0;
                font-size: 24px;
                font-weight: bold;
            }}
            .content {{
                margin-top: 40px;
            }}
            .content h1 {{
                font-size: 48px;
                margin-bottom: 16px;
                color: #10b981;
            }}
            .content p {{
                font-size: 18px;
                color: #374151;
            }}
            .car-icon {{
                margin-top: 40px;
                width: 120px;
                height: auto;
            }}
        </style>
    </head>
    <body>
        <div class="header">MUCHAS GRACIAS</div>
        <div class="content">
            <h1>¡GRACIAS!</h1>
            <p>Será redireccionado en un momento...</p>
            <img src="car.gif" class="car-icon" alt="Car Icon"/>
        </div>
    </body>
    </html>
    """
    return html
