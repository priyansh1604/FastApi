import pytesseract
import cv2
from pdf2image import convert_from_path
import re
from fastapi import FastAPI, UploadFile, File
import shutil
from typing import Union

app = FastAPI()

PAN_REGEX = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
AADHAAR_REGEX = r"\b\d{4}\s\d{4}\s\d{4}\b"

def extract_text_from_image(image_path: str) -> str:
    image = cv2.imread(image_path)

    height, width, _ = image.shape
    if width < 1000:
        image = cv2.resize(image, (1000, int(height * (1000 / width))))

    # Step 3: Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 4: Increase contrast using histogram equalization
    gray = cv2.equalizeHist(gray)

    # Step 5: Adaptive thresholding (adaptive to varying lighting)
    thresh = cv2.adaptiveThreshold(
        gray, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 2
    )

    # Optional: Save intermediate images for debugging
    cv2.imwrite("debug_gray.jpg", gray)
    cv2.imwrite("debug_thresh.jpg", thresh)

    # Step 4: OCR extraction with Tesseract
    custom_config = r'--oem 3 --psm 6'  # OEM 3 = LSTM mode, PSM 6 = Assume block of text
    text = pytesseract.image_to_string(thresh, config=custom_config)
    text2 =pytesseract.image_to_string(gray)
    print(f"Extracted Text: {text}")
    print(f"Extracted Text: {text2}")
    return text

def extract_text_from_pdf(pdf_path: str) -> str:
    images = convert_from_path(pdf_path)
    full_text = ""
    for i, image in enumerate(images):
        image.save(f"page_{i}.jpg", "JPEG")
        text = pytesseract.image_to_string(image)
        full_text += text
    return full_text

def detect_document_type_and_number(text: str) -> Union[dict, str]:
    if re.search(PAN_REGEX, text):
        pan_number = re.findall(PAN_REGEX, text)[0]
        return {"type": "PAN Card", "number": pan_number}
    elif re.search(AADHAAR_REGEX, text):
        aadhar_number = re.findall(AADHAAR_REGEX, text)[0]
        return {"type": "Aadhaar Card", "number": aadhar_number}
    else:
        return "Document type not recognized or number not found."

# API
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"uploaded_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    if file.filename.endswith((".jpg", ".jpeg", ".png")):
        extracted_text = extract_text_from_image(file_location)
    elif file.filename.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_location)
    else:
        return {"error": "Unsupported file format"}


    result = detect_document_type_and_number(extracted_text)
    return {"result": result}



#     def deskew(image):
#     coords = cv2.findNonZero(cv2.bitwise_not(image))
#     angle = cv2.minAreaRect(coords)[-1]
#     if angle < -45:
#         angle = -(90 + angle)
#     else:
#         angle = -angle
#     (h, w) = image.shape[:2]
#     center = (w // 2, h // 2)
#     M = cv2.getRotationMatrix2D(center, angle, 1.0)
#     rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
#     return rotated

# # Deskew before thresholding
# gray = deskew(gray)
# def extract_text_from_image(image_path: str) -> str:
#     image = cv2.imread(image_path)
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     cv2.imwrite("debug_output.jpg", gray)
#     text = pytesseract.image_to_string(gray)
    
#     print (text)
#     return text