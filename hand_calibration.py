import cv2
import numpy as np
import mediapipe as mp
from display_manager import DisplayManager

# Initialize mediapipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,  # False = video mode
                       max_num_hands=1,
                       min_detection_confidence=0.5,  # Minimum confidence for hand detection
                       min_tracking_confidence=0.5)  # Minimum confidence for hand tracking

# Utility for drawing hand landmarks
mp_drawing = mp.solutions.drawing_utils

# Set up camera capture (dependent on number of devices, revert to 0 if needed)
cap = cv2.VideoCapture(1)

# Get display settings
display = DisplayManager()
width, height = display.get_screen_dimensions()

# Define target points for calibration on the screen
target_points = [(100, 100), (width - 100, 100), (width - 100, height - 100), (100, height - 100)]
calibration_points = []

# Function to capture hand landmarks at the defined target points
def capture_hand_landmarks():
    global calibration_points
    calibration_points.clear()  # Clear any existing calibration points
    for i, point in enumerate(target_points):
        while True:
            # Create a blank image with a circle at the target point
            calibration_image = np.zeros((height, width, 3), dtype=np.uint8)
            cv2.circle(calibration_image, point, 20, (0, 0, 255), -1)
            cv2.putText(calibration_image, f'Point {i+1}', (point[0] + 30, point[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Show the calibration image in full screen
            cv2.namedWindow("Calibration Targets", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("Calibration Targets", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Calibration Targets", calibration_image)

            # Capture a frame from the camera
            ret, frame = cap.read()
            if not ret:
                continue

            # Convert the frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame to detect hand landmarks
            results = hands.process(rgb_frame)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Display the camera view with hand landmarks
            cv2.imshow("Camera View", frame)

            # Wait for the user to press Enter to capture the landmark
            key = cv2.waitKey(1)
            if key == 13:  # Enter key pressed
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Capture the index finger tip landmark (landmark 8)
                        x = int(hand_landmarks.landmark[8].x * frame.shape[1])
                        y = int(hand_landmarks.landmark[8].y * frame.shape[0])
                        calibration_points.append((x, y))  # Save the captured point
                        print(f"Captured hand landmark for Point {i+1} at: ({x}, {y})")
                        break
                else:
                    print("Error: No hand landmark detected. Please try again.")
                    continue
                break

# Capture hand landmarks at the defined target points
capture_hand_landmarks()
cv2.destroyAllWindows()  # Close all OpenCV windows

# Check if all calibration points are captured
if len(calibration_points) == 4:
    # Convert points to numpy arrays
    target_points_np = np.array(target_points, dtype=np.float32)
    calibration_points_np = np.array(calibration_points, dtype=np.float32)
    # Calculate the homography matrix
    M, _ = cv2.findHomography(calibration_points_np, target_points_np)
    # Save the homography matrix to a file for reference in other functions
    np.save("M.npy", M)
    print("Calibration successful. M matrix saved.")
else:
    print("Error: Not all calibration points were captured.")
