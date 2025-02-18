import pytesseract
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import re
import os

def ExtractDetails(image_path):
    # Load and preprocess the image
    text = pytesseract.image_to_string(Image.open(image_path), lang='eng')
    print(text)
    text = text.replace("\n", " ").replace("  ", " ")
    
    # Regex patterns for PAN number and DOB
    regex_DOB = re.compile(r'\d{2}[-/]\d{2}[-/]\d{4}')
    regex_num = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]{1}')
    
    # Load the image with OpenCV for display
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(image)
    plt.axis("off")
    #plt.show()

    # Extract and display PAN number
    pan_numbers = regex_num.findall(text)
    print(pan_numbers)
    if pan_numbers:
        print("PAN Card Number:", pan_numbers[0])
    else:
        print("Blurry image or PAN number not detected!")

    # Extract and display Date of Birth
    dob_matches = regex_DOB.findall(text)
    if dob_matches:
        print("Date of Birth:", dob_matches[0])
    else:
        print("Blurry image or Date of Birth not detected!")

# Run the function with your image path
ExtractDetails(r"C:\Users\priyansh\Desktop\docs\pan.jpg")
