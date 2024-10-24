import cv2
import numpy as np
from PIL import Image
import random

def capture_image():
    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return None, "Error: Unable to access the webcam."
    
    print("Press 'c' to capture an image...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return None, "Error: Failed to capture an image from the webcam."
        
        cv2.imshow('Webcam', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('c'):
            cv2.destroyAllWindows()
            cap.release()
            return frame, "Image captured successfully"
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            cap.release()
            return None, "Capture cancelled by user"

def detect_faces(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Load the face cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) == 0:
        return None, "No faces detected"
    
    # For simplicity, we'll use the first detected face
    (x, y, w, h) = faces[0]
    
    # Extract facial features
    face = img[y:y+h, x:x+w]
    
    # Convert to PIL Image
    face_pil = Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
    
    return face_pil, "Face detected and extracted"

def analyze_skin_tone(face_image):
    # Convert PIL Image to numpy array
    face_array = np.array(face_image)
    
    # Calculate average color
    average_color = np.mean(face_array, axis=(0, 1))
    
    # Simple classification based on average color
    if np.mean(average_color) > 200:
        return "fair"
    elif np.mean(average_color) > 150:
        return "medium"
    else:
        return "dark"

def get_makeup_recommendation(skin_tone):
    recommendations = {
        "fair": [
            "Use a light coverage foundation to even out skin tone.",
            "Opt for soft pink or peach blush for a natural flush.",
            "Choose light eyeshadows like champagne or soft brown.",
            "Use a light pink or nude lipstick."
        ],
        "medium": [
            "Use a medium coverage foundation that matches your skin tone.",
            "Try coral or rose blush for a healthy glow.",
            "Experiment with bronze or gold eyeshadows.",
            "Go for berry or mauve lipsticks."
        ],
        "dark": [
            "Use a full coverage foundation that matches your deep skin tone.",
            "Opt for deep orange or red blush for a vibrant look.",
            "Try bold eyeshadow colors like purple or emerald green.",
            "Experiment with deep red or plum lipsticks."
        ]
    }
    
    base_recommendation = f"For your {skin_tone} skin tone, here are some makeup recommendations:\n\n"
    specific_recommendations = "\n".join(f"- {rec}" for rec in recommendations[skin_tone])
    
    return base_recommendation + specific_recommendations

def main():
    # Capture image from webcam
    img, message = capture_image()
    
    if img is None:
        print(message)
        return
    
    print(message)
    
    # Detect face and extract features
    face_image, face_message = detect_faces(img)
    
    if face_image is None:
        print(face_message)
        return
    
    print(face_message)
    
    # Analyze skin tone
    skin_tone = analyze_skin_tone(face_image)
    
    # Get makeup recommendation
    recommendation = get_makeup_recommendation(skin_tone)
    
    print("\nMakeup Recommendation:")
    print(recommendation)

if __name__ == "__main__":
    main()