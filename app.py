import io
import easyocr
import re
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pdf2image import convert_from_bytes
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import cv2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace '*' with specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize EasyOCR reader
reader = easyocr.Reader(["en"])

# Function to extract text and PAN number from an image
def extract_text_from_image(image_bytes):
    # Convert image bytes to OpenCV format
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    # Preprocess the image
    gray = cv2.resize(image, None, fx=1.5, fy=1.5)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    
    # Extract text using EasyOCR
    results = reader.readtext(gray, detail=0)
    
    # Join extracted lines into a single block of text
    text = " ".join(results)
    
    pan_regex = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
    pan_number = re.findall(pan_regex, text)
    
    return {
        "extracted_text": text,
        "pan_number": pan_number[0] if pan_number else "PAN number not found"
    }
@app.get("/test")
async def hello():
    return JSONResponse("heyyy")

# @app.post("/upload/")
# async def upload_file(file: UploadFile = File(...)):
#     # Read the file content into memory
#     file_content = await file.read()

#     if file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
#         # Process image from the in-memory file content
#         result = extract_text_from_image(file_content)
#     elif file.filename.lower().endswith(".pdf"):
#         # Convert PDF to images in-memory and process each page
#         pages = convert_from_bytes(file_content)
#         all_text = ""
#         pan_numbers = set()

#         for page_num, page in enumerate(pages):
#             # Convert PIL image to bytes for OCR processing
#             image_bytes = io.BytesIO()
#             page.save(image_bytes, format='JPEG')
#             image_bytes.seek(0)
#             result = extract_text_from_image(image_bytes.read())
#             all_text += result["extracted_text"] + "\n"
#             if result["pan_number"] != "PAN number not found":
#                 pan_numbers.add(result["pan_number"])
#             truncated_text = all_text[:1000]

#         result = {
#             "extracted_text": truncated_text,
#             "pan_number": list(pan_numbers) if pan_numbers else "PAN number not found"
#         }
#     else:
#         return JSONResponse(
#             content={"error": "Unsupported file type. Please upload a PNG, JPG, or PDF."},
#             status_code=400
#         )

#     return JSONResponse(content=result)
