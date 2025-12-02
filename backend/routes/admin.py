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


