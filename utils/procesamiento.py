import cv2
import imutils
import re

def process_frame(frame, model, ocr):
    placa_limpia = None
    results = model(frame)

    for result in results:
        index_plates = (result.boxes.cls == 0).nonzero(as_tuple=True)[0]
    
        for idx in index_plates:
            conf = result.boxes.conf[idx].item()
            if conf > 0.4:
                xyxy = result.boxes.xyxy[idx].squeeze().tolist()
                x1, y1 = int(xyxy[0]), int(xyxy[1])
                x2, y2 = int(xyxy[2]), int(xyxy[3])

                plate_image = frame[y1-15:y2+15, x1-15:x2+15]

                try:
                    result_ocr = ocr.predict(cv2.cvtColor(plate_image, cv2.COLOR_BGR2RGB))

                    boxes = result_ocr[0]['rec_boxes']
                    texts = result_ocr[0]['rec_texts']
                    left_to_right = sorted(zip(boxes, texts), key=lambda x: min(x[0][::2]))

                    whitelist_pattern = re.compile(r'^[A-Z0-9]+$')
                    left_to_right = ''.join([t for _, t in left_to_right])
                    output_text = ''.join([t for t in left_to_right if whitelist_pattern.fullmatch(t) ])
                    placa_limpia = output_text[:6]

                except:
                    placa_limpia = ""

                cv2.rectangle(frame, (x1-10, y1-35), (x2+10, y2-(y2-y1)), (0, 255, 0), -1)
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(frame, placa_limpia, (x1-7, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,0), 2)

    return placa_limpia, frame