from flask import Flask, request, render_template, redirect
import numpy as np
import os
import cv2
import pytesseract
import re
from PIL import Image

# Initialize the Flask app
app = Flask(__name__)

# Route for the homepage
@app.route('/')
def index():
    return render_template('upload.html')

# Route for making predictions
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    # Save the uploaded file to the 'images' folder
    image_path = os.path.join('images', file.filename)
    file.save(image_path)
    
    # Debugging: print the image path
    print(f"Image saved at: {image_path}")
    
    # Ensure that the file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file {image_path} not found.")
        return "Error: Image not found", 500

    # Extract text from the image
    text = extract_text_from_image(image_path)
    
    # Example prediction (use model if necessary)
    prediction = text  # This is where you can use your ML model, if needed
    
    # Render results page with text and prediction
    return render_template('results.html', text=text, prediction=prediction, image_path=image_path)

# Function to preprocess the image (grayscale and thresholding)
def preprocess_image(image_path):
    try:
        img = Image.open(image_path).convert('L')  # Open and convert to grayscale
        img_np = np.array(img)  # Convert image to numpy array
        _, img_thresh = cv2.threshold(img_np, 150, 255, cv2.THRESH_BINARY)  # Threshold image
        return img_thresh
    except Exception as e:
        print(f"Error in preprocessing image {image_path}: {e}")
        return None

# Function to extract text from an image
def extract_text_from_image(image_path):
    try:
        # Preprocess the image to improve OCR accuracy
        img = preprocess_image(image_path)
        if img is None:
            return "Error processing image22"
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return "Error processing image"

# Function to preprocess and clean extracted entity values (if needed)
def preprocess_entity_value(value):
    try:
        # Ensure proper spacing between numbers and units
        value = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', value)

        # Check for range in list format [x, y] unit
        match = re.match(r"\[(\d+\.?\d*),\s*(\d+\.?\d*)\]\s+(\w+)", value)
        if match:
            start_number, end_number, unit = match.groups()
            return f"{start_number}-{end_number}", unit

        # Check for range in "x to y unit" format
        if ' to ' in value:
            start, end = value.split(' to ')
            start_number, start_unit = start.split(maxsplit=1)
            end_number, end_unit = end.split(maxsplit=1)

            if start_unit != end_unit:
                raise ValueError(f"Different units in range: {start_unit} and {end_unit}")

            return f"{start_number}-{end_number}", start_unit

        # Handle single value
        parts = value.split(maxsplit=1)
        if len(parts) != 2:
            raise ValueError(f"Invalid format in {value}")

        number = float(parts[0])
        unit = parts[1]
        return number, unit

    except ValueError as e:
        print(f"Error processing value '{value}': {e}")
        return None, None

if __name__ == '__main__':
    app.run(debug=True)
