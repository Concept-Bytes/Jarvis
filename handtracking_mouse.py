import cv2
import mediapipe as mp
import pyautogui as pag
import numpy as np




# Initialize Mediapipe Hand solution
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.1,
                       min_tracking_confidence=0.1)

mp_drawing = mp.solutions.drawing_utils

#open the camera
cap = cv2.VideoCapture(0)


# error check to make sure the camera is open
if not cap.isOpened():
    print("Error")
    exit()


# Set the screen resolution (width, height)
screen_width, screen_height = pag.size()

mouseDown = False

#Main loop
while True:

    #capture frame by frame from the camera
    success, frame = cap.read()
    if not success:
        break
    
    # Flip the frame horizontally 
    frame = cv2.flip(frame, 1)

    # Convert the frame color from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the RGB frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    #frame resoulution
    frame_height, frame_width, _ = frame.shape

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks,mp_hands.HAND_CONNECTIONS)

            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            #get the midpoint between the thumb and index finger
            midpoint_x = (index_finger_tip.x + thumb_tip.x) /2
            midpoint_y = (index_finger_tip.y + thumb_tip.y) /2

            # Get the distance between the thumb and index finger
            distance = np.sqrt((index_finger_tip.x - thumb_tip.x)**2 + (index_finger_tip.y - thumb_tip.y)**2)

            if distance < 0.1 and mouseDown == False:
                #mouse down
                pag.mouseDown()
                mouseDown = True
            if distance > 0.3 and mouseDown == True:
                #mouse up
                pag.mouseUp()
                mouseDown = False
            
            if mouseDown:
                #draw a circle at the midpoint with radius 10 (# of pixels )
                cv2.circle(frame, (int(midpoint_x*frame_width), int(midpoint_y * frame_height)), 10, (0, 255,0), -1)

            else:
                #draw a circle at the midpoint with radius 10
                cv2.circle(frame, (int(midpoint_x*frame_width), int(midpoint_y * frame_height)), 10, (0, 255,0), 1)
            

            # Map the position to the screen resolution
            x_mapped = np.interp(midpoint_x, (0,1), (0, screen_width))
            y_mapped = np.interp(midpoint_y, (0,1), (0, screen_height))

            # Set the mouse position
            pag.moveTo(x_mapped, y_mapped, duration= 0.1)
            
    # Display the resulting frame
    cv2.imshow("Medipipe Hands", frame)
    cv2.waitKey(1)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()



    



