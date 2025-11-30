import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR
from utils.processor import process_frame
from utils.client_update import send_plate_to_web

# Coordenadas normalizadas de las ROI
ROIS = {
    "slot6": (0.74, 0.05, 0.97, 0.17),
    "slot5": (0.74, 0.17, 0.97, 0.29),
    "slot4": (0.74, 0.29, 0.97, 0.41),
    "slot3": (0.74, 0.41, 0.97, 0.53),
    "slot2": (0.74, 0.53, 0.97, 0.65),
    "slot1": (0.74, 0.65, 0.97, 0.77),
    "entrada": (0.38, 0.58, 0.60, 0.82),
    "salida": (0.06, 0.08, 0.30, 0.28),
}

cap = cv2.VideoCapture(0)
model = YOLO("C:\\Users\\Lizeth\\OneDrive\\Escritorio\\v7-ANPR\\models\\best.pt")
ocr = PaddleOCR(use_angle_cls=True, lang="en")

def draw_rois(frame, rois):
    h, w, _ = frame.shape
    for name, (x1, y1, x2, y2) in rois.items():
        # Convertir coordenadas normalizadas a pixeles
        pt1 = (int(x1 * w), int(y1 * h))
        pt2 = (int(x2 * w), int(y2 * h))
        cv2.rectangle(frame, pt1, pt2, (0, 255, 0), 2)
        cv2.putText(frame, name, (pt1[0], pt1[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

def is_inside_roi(bbox, rois, frame_shape):
    """Verifica si el bbox de la placa cae dentro de alguna ROI"""
    h, w, _ = frame_shape
    px1, py1, px2, py2 = bbox
    for name, (x1, y1, x2, y2) in rois.items():
        rx1, ry1, rx2, ry2 = int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)
        # Comprobar intersección
        if not (px2 < rx1 or px1 > rx2 or py2 < ry1 or py1 > ry2):
            return name
    return None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    placa, frame_out, bbox = process_frame(frame, model, ocr, ROIS)  
    # 👆 Asegúrate que process_frame devuelva también el bbox de la placa detectada

    # Dibujar las ROI en el frame
    draw_rois(frame_out, ROIS)

    if placa and bbox:
        slot_detectado = is_inside_roi(bbox, ROIS, frame.shape)
        if slot_detectado:
            print(f"Placa detectada: {placa} en {slot_detectado}")
            send_plate_to_web(placa)  # luego aquí añadimos el slot

    cv2.imshow("ANPR", frame_out)

    if cv2.waitKey(1) & 0xFF in [ord('q'), 27]: # 'q o 'ESC' para salir
        break

cap.release()
cv2.destroyAllWindows()