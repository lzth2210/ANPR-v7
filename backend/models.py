from flask_sqlalchemy import SQLAlchemy
import serial
import time

db = SQLAlchemy()

# Inicializar puerto serial global
ser = serial.Serial('COM8', 9600, timeout=1)
time.sleep(2)
# Inicializar servo en estado R (reposo/cerrado)
ser.write(b'R')
time.sleep(1)

class PlateRecord(db.Model):
    __tablename__ = "plates"

    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(20), nullable=False)
    slot = db.Column(db.String(20))
    timestamp = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "plate": self.plate,
            "slot": self.slot,
            "timestamp": self.timestamp
        }