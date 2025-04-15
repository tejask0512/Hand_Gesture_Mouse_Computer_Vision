import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Initialize MediaPipe Hand solution
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# Screen dimensions
screen_width, screen_height = pyautogui.size()

# Smoothing factor for mouse movement
smoothing = 5
prev_x, prev_y = 0, 0

# Finger tap detection parameters
tap_threshold = 0.3  # Distance threshold for tap detection
last_index_tap_time = 0
last_middle_tap_time = 0
tap_cooldown = 0.5  # Seconds between taps

# Get webcam
cap = cv2.VideoCapture(0)

def detect_finger_tap(landmarks, finger_tip_idx, finger_pip_idx):
    """Detect if a finger is tapped (tip close to palm)"""
    tip = landmarks[finger_tip_idx]
    pip = landmarks[finger_pip_idx]
    
    # Calculate vertical distance between tip and pip
    distance = abs(tip.y - pip.y)
    
    # If tip is below pip and close enough, it's a tap
    return tip.y > pip.y and distance < tap_threshold

def main():
    global prev_x, prev_y, last_index_tap_time, last_middle_tap_time
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Failed to capture image from webcam.")
            continue
        
        # Flip the image horizontally for a more intuitive mirror view
        image = cv2.flip(image, 1)
        
        # Convert BGR image to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image and detect hands
        results = hands.process(rgb_image)
        
        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Get the landmarks as a list
                landmarks = hand_landmarks.landmark
                
                # Index finger
                index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_pip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP]
                
                # Middle finger
                middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                middle_pip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
                
                # Wrist position for hand movement reference
                wrist = landmarks[mp_hands.HandLandmark.WRIST]
                
                # Mouse movement based on index finger position
                x = int(wrist.x * screen_width)
                y = int(wrist.y * screen_height)
                
                # Apply smoothing
                prev_x = prev_x + (x - prev_x) / smoothing
                prev_y = prev_y + (y - prev_y) / smoothing
                
                # Move the mouse
                pyautogui.moveTo(prev_x, prev_y)
                
                # Detect index finger tap for left click
                if detect_finger_tap(landmarks, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP):
                    current_time = time.time()
                    if current_time - last_index_tap_time > tap_cooldown:
                        print("Left click")
                        pyautogui.click()
                        last_index_tap_time = current_time
                
                # Detect middle finger tap for right click
                if detect_finger_tap(landmarks, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP):
                    current_time = time.time()
                    if current_time - last_middle_tap_time > tap_cooldown:
                        print("Right click")
                        pyautogui.rightClick()
                        last_middle_tap_time = current_time
        
        # Display the image with annotations
        cv2.imshow('Gesture Mouse Control', image)
        
        # Exit on 'q' press
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()