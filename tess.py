import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

image = cv2.imread('.\\placa.jpg')

text = pytesseract.image_to_string(image, config='--psm 7')

print(text)

cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()