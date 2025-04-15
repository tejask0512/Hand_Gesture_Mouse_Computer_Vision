import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import json
import os

# Initialize MediaPipe Hand solution
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# Get screen dimensions for mapping hand position to screen coordinates
screen_width, screen_height = pyautogui.size()

# Prevent mouse from moving to screen edges
pyautogui.FAILSAFE = False

# Global variables for mouse movement
prev_x, prev_y = screen_width // 2, screen_height // 2
smoothing = 5  # Smoothing factor for cursor movement

# Variables for gesture detection
tap_threshold = 0.03  # Threshold for detecting finger taps
last_index_tap_time = 0  # Last time index finger was tapped
last_middle_tap_time = 0  # Last time middle finger was tapped
tap_cooldown = 0.5  # Seconds to wait between taps

# New variables for scrolling
scroll_active = False
scroll_start_y = 0
last_scroll_time = 0
scroll_cooldown = 0.05  # Seconds between scroll actions
scroll_sensitivity = 1.0  # Default scroll sensitivity

# New variables for mouse sensitivity
mouse_sensitivity = 1.0  # Default value
sensitivity_min = 0.2    # Minimum allowed sensitivity
sensitivity_max = 3.0    # Maximum allowed sensitivity
sensitivity_step = 0.1   # Increment/decrement step
last_sensitivity_change_time = 0
sensitivity_change_cooldown = 1.0  # Seconds between adjustments

# Config file for saving settings
config_file = "gesture_mouse_config.json"

def load_settings():
    """Load settings from a JSON file if it exists"""
    global mouse_sensitivity, scroll_sensitivity, smoothing
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                settings = json.load(f)
            
            mouse_sensitivity = settings.get("mouse_sensitivity", mouse_sensitivity)
            scroll_sensitivity = settings.get("scroll_sensitivity", scroll_sensitivity)
            smoothing = settings.get("smoothing", smoothing)
            
            print("Settings loaded!")
        except:
            print("Error loading settings. Using defaults.")

def save_settings():
    """Save current settings to a JSON file"""
    settings = {
        "mouse_sensitivity": mouse_sensitivity,
        "scroll_sensitivity": scroll_sensitivity,
        "smoothing": smoothing
    }
    
    with open(config_file, 'w') as f:
        json.dump(settings, f)
    
    print("Settings saved!")

def detect_finger_tap(landmarks, finger_tip_idx, finger_pip_idx):
    """Detect if a finger is tapped (tip close to palm)"""
    tip = landmarks[finger_tip_idx]
    pip = landmarks[finger_pip_idx]
    
    # Calculate vertical distance between tip and pip
    distance = abs(tip.y - pip.y)
    
    # If tip is below pip and close enough, it's a tap
    return tip.y > pip.y and distance < tap_threshold

def detect_scroll_gesture(landmarks):
    """Detect thumb and ring finger pinch for scrolling"""
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    
    # Calculate distance between thumb and ring finger
    distance = np.sqrt((thumb_tip.x - ring_tip.x)**2 + (thumb_tip.y - ring_tip.y)**2)
    
    # If thumb and ring finger are close enough, it's a pinch
    return distance < 0.07  # Threshold value may need adjustment

def detect_two_finger_scroll(landmarks):
    """Detect index and middle finger extended for scrolling"""
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_pip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
    
    # Check if both fingers are extended (tips above pips)
    index_extended = index_tip.y < index_pip.y
    middle_extended = middle_tip.y < middle_pip.y
    
    # Check if other fingers are curled
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_pip = landmarks[mp_hands.HandLandmark.RING_FINGER_PIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]
    pinky_pip = landmarks[mp_hands.HandLandmark.PINKY_PIP]
    
    ring_curled = ring_tip.y > ring_pip.y
    pinky_curled = pinky_tip.y > pinky_pip.y
    
    # Return true if index and middle extended, others curled
    return index_extended and middle_extended and ring_curled and pinky_curled

def detect_increase_sensitivity_gesture(landmarks):
    """Detect gesture for increasing sensitivity (pinky and thumb pinch)"""
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]
    
    distance = np.sqrt((thumb_tip.x - pinky_tip.x)**2 + (thumb_tip.y - pinky_tip.y)**2)
    return distance < 0.07

def detect_decrease_sensitivity_gesture(landmarks):
    """Detect gesture for decreasing sensitivity (thumb touching wrist)"""
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    wrist = landmarks[mp_hands.HandLandmark.WRIST]
    
    distance = np.sqrt((thumb_tip.x - wrist.x)**2 + (thumb_tip.y - wrist.y)**2)
    return distance < 0.12

def apply_scroll_curve(movement):
    """Apply a non-linear curve to make small movements more precise"""
    # Square the movement but keep the sign
    sign = 1 if movement >= 0 else -1
    magnitude = abs(movement)
    
    # Apply curve: square for values > 0.1, linear for smaller values
    if magnitude > 0.1:
        result = sign * ((magnitude - 0.1) ** 2) * 2 + (sign * 0.1)
    else:
        result = sign * magnitude
    
    return result

def create_control_window():
    """Create a control window with sliders for sensitivity adjustment"""
    cv2.namedWindow('Mouse Controls')
    cv2.createTrackbar('Sensitivity', 'Mouse Controls', 
                       int(mouse_sensitivity * 10), 
                       int(sensitivity_max * 10), 
                       on_sensitivity_change)
    cv2.createTrackbar('Scroll Speed', 'Mouse Controls', 
                       int(scroll_sensitivity * 10), 
                       int(sensitivity_max * 10), 
                       on_scroll_sensitivity_change)

def on_sensitivity_change(value):
    """Callback for mouse sensitivity slider"""
    global mouse_sensitivity
    mouse_sensitivity = value / 10.0

def on_scroll_sensitivity_change(value):
    """Callback for scroll sensitivity slider"""
    global scroll_sensitivity
    scroll_sensitivity = value / 10.0

# Load saved settings
load_settings()

# Create control window
create_control_window()

# Get webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Failed to capture image from webcam.")
        continue
    
    # Flip the image horizontally for a more intuitive mirror view
    image = cv2.flip(image, 1)
    
    # Convert BGR image to RGB for MediaPipe
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process the image and detect hands
    results = hands.process(rgb_image)
    
    # Draw hand landmarks if detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get the landmarks as a list
            landmarks = hand_landmarks.landmark
            
            # Mouse movement using wrist position
            wrist = landmarks[mp_hands.HandLandmark.WRIST]
            
            # Get raw coordinates
            raw_x = wrist.x * screen_width
            raw_y = wrist.y * screen_height
            
            # Calculate center of screen
            center_x = screen_width / 2
            center_y = screen_height / 2
            
            # Apply sensitivity to the distance from center
            offset_x = (raw_x - center_x) * mouse_sensitivity
            offset_y = (raw_y - center_y) * mouse_sensitivity
            
            # Calculate final position
            x = int(center_x + offset_x)
            y = int(center_y + offset_y)
            
            # Apply smoothing for stable cursor movement
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
            
            # Check for scroll gesture
            is_scroll_gesture = detect_scroll_gesture(landmarks)
            
            # Get middle point between thumb and ring finger for tracking
            if is_scroll_gesture:
                thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
                ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
                current_y = (thumb_tip.y + ring_tip.y) / 2
                
                # Draw a visual indicator for active scrolling
                cv2.circle(image, (50, 50), 20, (0, 255, 0), -1)  # Green circle when scrolling
                
                # Initialize scroll if just started pinching
                if not scroll_active:
                    scroll_active = True
                    scroll_start_y = current_y
                else:
                    # Calculate scroll distance
                    current_time = time.time()
                    if current_time - last_scroll_time > scroll_cooldown:
                        # Convert movement to scroll amount
                        movement = current_y - scroll_start_y
                        # Apply non-linear curve and sensitivity
                        scroll_amount = int(apply_scroll_curve(movement) * 20 * scroll_sensitivity)
                        
                        if abs(scroll_amount) > 0:
                            # Scroll direction text
                            direction = "UP" if scroll_amount < 0 else "DOWN"
                            cv2.putText(image, f"Scrolling {direction}", 
                                       (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            # Scroll up or down
                            pyautogui.scroll(-scroll_amount)  # Negative because screen coordinates are inverted
                            scroll_start_y = current_y  # Reset start position
                            last_scroll_time = current_time
            else:
                scroll_active = False
            
            # Check for sensitivity adjustment gestures
            current_time = time.time()
            if current_time - last_sensitivity_change_time > sensitivity_change_cooldown:
                if detect_increase_sensitivity_gesture(landmarks):
                    mouse_sensitivity = min(mouse_sensitivity + sensitivity_step, sensitivity_max)
                    print(f"Sensitivity increased to: {mouse_sensitivity:.1f}")
                    cv2.setTrackbarPos('Sensitivity', 'Mouse Controls', int(mouse_sensitivity * 10))
                    last_sensitivity_change_time = current_time
                
                elif detect_decrease_sensitivity_gesture(landmarks):
                    mouse_sensitivity = max(mouse_sensitivity - sensitivity_step, sensitivity_min)
                    print(f"Sensitivity decreased to: {mouse_sensitivity:.1f}")
                    cv2.setTrackbarPos('Sensitivity', 'Mouse Controls', int(mouse_sensitivity * 10))
                    last_sensitivity_change_time = current_time
    
    # Display current sensitivity on screen
    cv2.putText(image, f"Mouse Sensitivity: {mouse_sensitivity:.1f}", 
                (10, image.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, (0, 255, 0), 2)
    cv2.putText(image, f"Scroll Sensitivity: {scroll_sensitivity:.1f}", 
                (10, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, (0, 255, 0), 2)
    
    # Display the image
    cv2.imshow('Gesture Mouse Control', image)
    
    # Process keyboard input
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC key to exit
        break
    elif key == ord('s'):  # 's' key to save settings
        save_settings()

# Release resources
cap.release()
cv2.destroyAllWindows()