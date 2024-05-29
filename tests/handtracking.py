import cv2
import mediapipe as mp

# Initialize Mediapipe Hand solution
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(static_image_mode=False,
                        max_num_hands=2,
                        min_detection_confidence=0.1,
                        min_tracking_confidence=0.1)

# Trace hand tracking visually
mp_drawing = mp.solutions.drawing_utils

# Select camera, try 0, 1 or 2 depending on which camera you want to use
cap = cv2.VideoCapture(0)

# Error check to make sure the camera is open
if not cap.isOpened():
    print("Error")
    exit()

#  Main loop e.g. continously grab frames from opencv, send them to mediapipe, display them with opencv
while True:

    # Capture frame by frame from the camera
    # Success = BOOLEAN
    success, frame = cap.read()
    if not success:
        break
    
    # Flip the frame horizontally (optional, depends on how camera is set up)
    frame = cv2.flip(frame, 1)

    # Convert the frame color from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the RGB frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    # Draw the hand annotations on the frame. Uses red dot for each joint, connected by white line
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw Landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Display the resulting frame
    cv2.imshow("Frame", frame)
    # Number of milliseconds to wait between frames
    cv2.waitKey(1)

# Release camera so it can be used for other things
cap.release()
# Turn off cv2 window 
cv2.destroyAllWindows()
