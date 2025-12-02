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
with app.app_context():
    db.create_all()

from routes.update_plate import plates_bp
from routes.factura import factura_bp
from routes.buscar import buscar_bp
from routes.admin import admin_bp
from routes.tabla import tabla_bp

# Registrar los blueprints
app.register_blueprint(plates_bp)
app.register_blueprint(factura_bp)
app.register_blueprint(buscar_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(tabla_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)