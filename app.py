import os
import shutil
import easyocr
import re
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pdf2image import convert_from_path
import tempfile

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize EasyOCR reader
reader = easyocr.Reader(["en"])

# Function to extract text and PAN number from an image
def extract_text_from_image(image_path):
    import cv2
    
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=1.5, fy=1.5)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    
    # Extract text using EasyOCR
    results = reader.readtext(gray, detail=0)
    
    # Join extracted lines into a single block of text
    text = " ".join(results)
    print("Extracted Text:", text)
    
    pan_regex = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
    pan_number = re.findall(pan_regex, text)
    
    return {
        "extracted_text": text,
        "pan_number": pan_number[0] if pan_number else "PAN number not found"
    }

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        # Process image
        result = extract_text_from_image(file_path)
    elif file.filename.lower().endswith(".pdf"):
        # Convert PDF to images and process each page
        pages = convert_from_path(file_path)
        all_text = ""
        pan_numbers = set()

        for page_num, page in enumerate(pages):
            image_path = f"{UPLOAD_FOLDER}/page_{page_num}.jpg"
            page.save(image_path, "JPEG")
            result = extract_text_from_image(image_path)
            all_text += result["extracted_text"] + "\n"
            if result["pan_number"] != "PAN number not found":
                pan_numbers.add(result["pan_number"])

        result = {
            "extracted_text": all_text,
            "pan_number": list(pan_numbers) if pan_numbers else "PAN number not found"
        }
    else:
        return JSONResponse(
            content={"error": "Unsupported file type. Please upload a PNG, JPG, or PDF."},
            status_code=400
        )

    # Clean up uploaded files after processing
    # os.remove(file_path)
    
    return JSONResponse(content=result)
