from flask import Blueprint, request, jsonify
from models import db, PlateRecord, ser
import time

plates_bp = Blueprint('plates', __name__)

def is_valid_plate(plate):
    """
    Valida que una placa sea válida:
    - No sea '???-???'
    - Tenga exactamente 6 caracteres
    """
    if not plate:
        return False
    # Filtrar placas inválidas
    if plate == "???-???" or plate == "???":
        return False
    # Debe tener exactamente 6 caracteres
    if len(plate) != 6:
        return False
    return True

@plates_bp.route('/update_plate', methods=['POST'])
def update_plate():
    data = request.get_json(force=True)
    plate = data.get("plate")
    slot = data.get("slot")

    if not plate or not is_valid_plate(plate):
        ser.write(b'R')
        return jsonify({"success": False, "error": "no plate o placa inválida"}), 400

    # -----------------------
    # 1) ENTRADA -> registrar
    # -----------------------
    if slot == "entrada":
        ser.write(b'V')
        time.sleep(4)
        ser.write(b'R')

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

    if slot.startswith("slot"):
    # slot viene como "slot1", "slot2", etc.
    
        slot_number = slot[-1]  # toma el último carácter
        command_map = {
            "1": b'A',
            "2": b'B',
            "3": b'C',
            "4": b'D',
            "5": b'E',
            "6": b'F'
        }
        ser.write(command_map[slot_number])

    if slot == "pagado":
        ser.write(b'V')
        time.sleep(4)
        ser.write(b'R')

        # Buscar el registro anterior (antes de crear el de "pagado")
        # que contiene el slot donde estaba el vehículo
        if last and last.slot.startswith("slot"):
            slot_number = last.slot[-1]  # ej: "slot3" → "3"
            command_map = {
                "1": b'G',
                "2": b'H',
                "3": b'I',
                "4": b'J',
                "5": b'K',
                "6": b'L'
            }
            ser.write(command_map[slot_number])

    return jsonify({"success": True, "info": "slot updated"}), 200