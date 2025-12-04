from flask import Blueprint, request, jsonify
from models import db, PlateRecord
import time

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
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
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8" />
            <title>Vista Administrador</title>
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
                }
                .header {
                    background-color: #3b82f6;
                    color: white;
                    width: 100%;
                    padding: 20px 0;
                    font-size: 28px;
                    font-weight: bold;
                    text-align: center;
                }
                .admin-panel {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 24px;
                    padding: 40px 20px;
                    width: 100%;
                    max-width: 1200px;
                }
                .stream-box {
                    background: white;
                    border-radius: 16px;
                    padding: 24px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    flex: 1 1 400px;
                    min-width: 300px;
                }
                .stream-box h3 {
                    text-align: center;
                    margin-bottom: 16px;
                    color: #1f2937;
                }
                iframe {
                    display: block;
                    margin: 0 auto;
                    border-radius: 8px;
                }
                .table-box {
                    background: #3b82f6;
                    border-radius: 16px;
                    padding: 24px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    flex: 1 1 600px;
                    min-width: 300px;
                    color: white;
                }
                .table-box h3 {
                    text-align: center;
                    margin-bottom: 16px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    background: white;
                    color: #111827;
                    border-radius: 8px;
                    overflow: hidden;
                }
                th, td {
                    padding: 12px;
                    text-align: center;
                    border-bottom: 1px solid #e5e7eb;
                }
                th {
                    background-color: #1f5fbf;
                    color: white;
                }
                tr:last-child td {
                    border-bottom: none;
                }
            </style>
        </head>
        <body>
            <div class="header">ADMINISTRADOR</div>
            <div class="admin-panel">
                <div class="stream-box">
                    <h3>Transmisión en vivo</h3>
                    <iframe src="http://tu-streaming-url" width="100%" height="360" frameborder="0" allowfullscreen></iframe>
                </div>
                <div class="table-box">
                    <h3>Tabla de Placas</h3>
                    <table>
                        <tr><th>ID</th><th>Placa</th><th>Slot</th><th>Hora</th></tr>
        """

        for r in records:
            hora = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r.timestamp))
            html += f"<tr><td>{r.id}</td><td>{r.plate}</td><td>{r.slot}</td><td>{hora}</td></tr>"

        html += """
                    </table>
                </div>
            </div>
        </body>
        </html>
        """
        return html

@admin_bp.route('/login', methods=['GET', 'POST'])
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
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8" />
        <title>Inicia Sesión</title>
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
                font-size: 28px;
                font-weight: bold;
                text-align: center;
            }
            .login-box {
                background: white;
                border-radius: 16px;
                padding: 40px 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-top: 60px;
                width: 100%;
                max-width: 400px;
                text-align: center;
            }
            .login-box h2 {
                margin-bottom: 16px;
                color: #10b981;
            }
            .login-box p {
                margin-bottom: 24px;
                font-size: 16px;
                color: #374151;
            }
            input[type="text"],
            input[type="password"] {
                width: 100%;
                padding: 12px;
                margin-bottom: 16px;
                border: 2px solid #3b82f6;
                border-radius: 8px;
                font-size: 16px;
                outline: none;
            }
            button {
                width: 100%;
                padding: 12px;
                background-color: #3b82f6;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: background 0.2s ease;
            }
            button:hover {
                background-color: #2563eb;
            }
        </style>
    </head>
    <body>
        <div class="header">INICIA SESIÓN</div>
        <div class="login-box">
            <h2>BIENVENIDO</h2>
            <p>Inserte el usuario y la contraseña:</p>
            <form method="post">
                <input type="text" name="username" placeholder="Usuario" required />
                <input type="password" name="password" placeholder="Contraseña" required />
                <button type="submit">ENTRAR</button>
            </form>
        </div>
    </body>
    </html>
    """

