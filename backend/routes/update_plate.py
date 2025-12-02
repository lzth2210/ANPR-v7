from flask import Blueprint, request, jsonify
from models import db, PlateRecord
import time

plates_bp = Blueprint('plates', __name__)

@plates_bp.route('/update_plate', methods=['POST'])
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

