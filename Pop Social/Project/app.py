#P Flask App

import os
import io
import csv
import time
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify, render_template
from keras.models import load_model
# Import the pre-trained model


# Create Flask application
app = Flask(__name__)

# Load the pre-trained model
model = model = load_model('Model/Image_Classification_Model.h5')

# List of class labels (mapping the class indices to human-readable labels)
class_labels = ["Airplane", "Automobile", "Bird", "Cat", "Deer", "Dog", "Frog", "Horse", "Ship", "Truck"]

def load_and_preprocess_image(image_file):
    img = Image.open(image_file)
    img = img.resize((32, 32))  # Resize to CIFAR-10 image size (32x32)
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def get_class_name(img_array):
    predictions = model.predict(img_array)
    top_prediction_index = np.argmax(predictions[0])
    class_name = class_labels[top_prediction_index]
    return class_name


# Function to save API request data to a CSV file
def save_api_request(request_data, response_data, time_taken):
    csv_file = 'static/Data_Storage/Events.csv'

    # Check if the CSV file exists, otherwise create it and write the header
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'IP Address', 'User-Agent', 'Username', 'Image File', 'Predicted Class', 'Time Taken'])

    # Get timestamp and user information (you may adapt this based on your authentication mechanism)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    ip_address = request_data.remote_addr
    user_agent = request_data.user_agent.string
    username = 'Guest'  # Replace this with actual user identification

    # Get the filename of the uploaded image (if available)
    image_file = request.files.get('image')
    filename = image_file.filename if image_file else 'N/A'

    # Get the predicted class from the response data
    predicted_class = response_data.get('class', 'N/A')

    # Append the request data to the CSV file
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip_address, user_agent, username, filename, predicted_class, time_taken])

# Home page with form to upload an image
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', prediction=None)

# Endpoint for image classification via HTML form

@app.route('/classify', methods=['POST'])
def classify_image():
    try:
        # Record the start time
        start_time = time.time()

        # Get the image from the request
        file = request.files['image']
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400

        # Save the image to the 'uploads' folder
        image_path = os.path.join('static', 'uploads', file.filename)
        file.save(image_path)

        # Load and preprocess the image
        img_array = load_and_preprocess_image(image_path)

        # Get class name prediction
        class_name = get_class_name(img_array)

        # Prepare response with prediction and filename
        prediction = {'class': class_name, 'filename': file.filename}
        # Calculate the time taken for the full request
        time_taken = time.time() - start_time
        # Save API request data to CSV
        save_api_request(request, prediction, time_taken)

        return render_template('index.html', prediction=prediction)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint for image classification via RESTful API
@app.route('/api/classify', methods=['POST'])
def classify_image_api():
    try:
        # Record the start time
        start_time = time.time()
        # Get the image from the request
        file = request.files['image']
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400

        # Load and preprocess the image
        img_array = load_and_preprocess_image(file)

        # Get class name prediction
        class_name = get_class_name(img_array)

        # Prepare response with prediction
        prediction = {'class': class_name}

        # Calculate the time taken for the full request
        time_taken = time.time() - start_time

        # Save API request data to CSV
        save_api_request(request, prediction, time_taken)
        
        return jsonify(prediction)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



