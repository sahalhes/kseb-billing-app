import cv2
import numpy as np
import pytesseract
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Mock tariff (replace with actual tariff structure)
tariff = {
    'fixed_charge': 50,
    'per_unit_charge': 5
}

@app.route('/upload', methods=['POST'])
def upload_meter_reading():
    consumer_number = request.form['consumer_number']
    image = request.files['meter_image']
    
    # Process the image
    img = Image.open(io.BytesIO(image.read()))
    reading = process_image(img)
    
    # Calculate bill
    bill = calculate_bill(reading)
    
    return jsonify({
        'consumer_number': consumer_number,
        'reading': reading,
        'bill_amount': bill
    })

def process_image(image):
    # Convert PIL Image to OpenCV format
    imgArr_o = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Convert to HSV color space
    imgArr = cv2.cvtColor(imgArr_o, cv2.COLOR_BGR2HSV)
    
    # Define range of green color in HSV
    roi_lower = np.array([40, 25, 0])
    roi_upper = np.array([80, 255, 255])
    
    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(imgArr, roi_lower, roi_upper)
    
    # Bitwise-AND mask and original image
    imgArr = cv2.bitwise_and(imgArr_o, imgArr_o, mask=mask)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
    
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        wbuffer = int(0.75 * w)
        hbuffer = int(0.1 * h)
        imgArr_ext = imgArr_o[y:y + h + hbuffer, x:x + w + wbuffer]
        
        imgArr_ext_gray = cv2.cvtColor(imgArr_ext, cv2.COLOR_BGR2GRAY)
        imgArr_ext_pp = cv2.adaptiveThreshold(imgArr_ext_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 199, 5)
        imgArr_ext_pp = cv2.medianBlur(imgArr_ext_pp, 13)
        
        # Perform OCR on the processed image
        reading = pytesseract.image_to_string(imgArr_ext_pp, config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
        
        # Extract numeric reading
        numeric_reading = ''.join(filter(str.isdigit, reading))
        
        if numeric_reading:
            return numeric_reading
    
    return "Error: Unable to extract reading"

def calculate_bill(reading):
    try:
        units = float(reading)
        bill = tariff['fixed_charge'] + (units * tariff['per_unit_charge'])
        return bill
    except ValueError:
        return "Error: Invalid reading"

if __name__ == '__main__':
    app.run(debug=True)