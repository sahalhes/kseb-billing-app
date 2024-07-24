import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Hugging Face API configuration
API_URL = "https://api-inference.huggingface.co/models/microsoft/trocr-large-printed"
headers = {"Authorization": "Bearer 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"}

tariff = {
    'fixed_charge': 260,
    'per_unit_charge': [
        {'unit': 100, 'rate': 3.25},
        {'unit': 100, 'rate': 4.05},
        {'unit': 100, 'rate': 5.10},
        {'unit': 100, 'rate': 6.95},
        {'unit': 100, 'rate': 8.20}
    ],
    'fuel_surcharge': 45,
    'monthly_fuel_surcharge': 50,
    'meter_rent': 12,
    'meter_rent_cgst': 1.08,
    'meter_rent_sgst': 1.08,
    'energy_duty': 275.5,
    'round_off': 0.34
}

def query_huggingface(image_data):
    response = requests.post(API_URL, headers=headers, data=image_data)
    return response.json()

@app.route('/upload', methods=['POST'])
def upload_meter_reading():
    consumer_number = request.form['consumer_number']
    image = request.files['meter_image']
    
    # Read the image data
    image_data = image.read()
    
    # Process the image using Hugging Face API
    reading = process_image(image_data)
    
    if isinstance(reading, str) and reading.startswith("Error"):
        return jsonify({
            'consumer_number': consumer_number,
            'reading': reading,
            'bill_details': "Error: Unable to calculate bill due to invalid reading"
        })

    # Calculate bill
    bill = calculate_bill(reading)
    
    return jsonify({
        'consumer_number': consumer_number,
        'reading': reading,
        'bill_details': f"{bill:.2f}"  # Ensure bill is formatted to 2 decimal places
    })

def process_image(image_data):
    # Query Hugging Face API
    result = query_huggingface(image_data)
    
    # Extract the text from the result
    if isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
        text = result[0]['generated_text']
        print(f"Extracted text: {text}")  # Debug statement
        # Extract numeric reading
        numeric_reading = ''.join(filter(str.isdigit, text))
        if numeric_reading:
            print(f"Numeric reading: {numeric_reading}")  # Debug statement
            return int(numeric_reading)
    
    return "Error: Unable to extract reading"

def calculate_bill(reading):
    try:
        units = float(reading)
        print(f"Units: {units}")  # Debug statement
        energy_charge = 0
        remaining_units = units
        
        for slab in tariff['per_unit_charge']:
            if remaining_units > slab['unit']:
                energy_charge += slab['unit'] * slab['rate']
                remaining_units -= slab['unit']
            else:
                energy_charge += remaining_units * slab['rate']
                break
        
        # Adding all other charges
        total_bill = (
            energy_charge +
            tariff['fixed_charge'] +
            tariff['fuel_surcharge'] +
            tariff['monthly_fuel_surcharge'] +
            tariff['meter_rent'] +
            tariff['meter_rent_cgst'] +
            tariff['meter_rent_sgst'] +
            tariff['energy_duty'] +
            tariff['round_off']
        )
        
        print(f"Total bill: {total_bill}")  # Debug statement
        return total_bill
    except ValueError:
        return "Error: Invalid reading"

if __name__ == '__main__':
    app.run(debug=True)
