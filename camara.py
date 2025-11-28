import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR
from main import process_frame
from client_update import send_plate_to_web

cap = cv2.VideoCapture(0)
model = YOLO("best.pt")
ocr = PaddleOCR(use_angle_cls=True, lang="en")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    placa, frame_out = process_frame(frame, model, ocr)

    if placa:
        print("Placa detectada: " + placa)
        send_plate_to_web(placa)

    cv2.imshow("ANPR", frame_out)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()