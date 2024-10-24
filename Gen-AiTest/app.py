from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import cv2
import base64
import numpy as np
import os
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
from PIL import Image
import io

app = Flask(__name__)
app.secret_key = '8f42a73054b1749f8f58848be5e6502c'

# Configure the Gemini API
genai.configure(api_key='AIzaSyAYb_NV_Gz2D7RDWR8auhOW-VqWUu3fjds')  # Replace with your actual API key

# Simple user database (replace with a real database in production)
users = {}

# Load the pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and check_password_hash(users[username], password):
        session['username'] = username
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    if username in users:
        return jsonify({'success': False, 'message': 'Username already exists'})
    users[username] = generate_password_hash(password)
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    image_data = request.json['image']
    image_bytes = base64.b64decode(image_data.split(',')[1])
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

    _, buffer = cv2.imencode('.jpg', image)
    processed_image = base64.b64encode(buffer).decode('utf-8')

    return jsonify({'processed_image': processed_image})

@app.route('/save_image', methods=['POST'])
def save_image():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    image_data = request.json['image']
    image_bytes = base64.b64decode(image_data.split(',')[1])
    
    user_dir = os.path.join('user_images', session['username'])
    os.makedirs(user_dir, exist_ok=True)
    
    image_path = os.path.join(user_dir, f'image_{len(os.listdir(user_dir)) + 1}.jpg')
    with open(image_path, 'wb') as f:
        f.write(image_bytes)
    
    return jsonify({'success': True, 'message': 'Image saved successfully'})

@app.route('/delete_image', methods=['POST'])
def delete_image():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    image_name = request.json['image_name']
    image_path = os.path.join('user_images', session['username'], image_name)
    
    if os.path.exists(image_path):
        os.remove(image_path)
        return jsonify({'success': True, 'message': 'Image deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Image not found'})

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    image_data = request.json['image']
    image_bytes = base64.b64decode(image_data.split(',')[1])
    
    # Convert image bytes to PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    
    # Generate content using Gemini
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([
        "Analyze this facial image and provide makeup and accessory recommendations based on the person's facial features. Focus only on makeup and accessories suitable for this face.",
        image
    ])
    
    return jsonify({
        'success': True,
        'recommendations': response.text
    })

if __name__ == '__main__':
    app.run(debug=True)
