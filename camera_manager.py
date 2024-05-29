import cv2
import numpy as np
import mediapipe as mp
from display_manager import DisplayManager

class CameraManager:
    def __init__(self, transformation_matrix_path):
        """
        Initialize the CameraManager class. 
        Uses OpenCV to capture frames for hand tracking.
        
        Parameters:
        - transformation_matrix_path: Path to the transformation matrix file (M.npy)
        """
        # Get display settings
        display = DisplayManager()
        self.width, self.height = display.get_screen_dimensions()
        self.cap = cv2.VideoCapture(1)  # Initialize camera capture (dependent on number of devices, revert to 0 if needed)
        self.M = np.load(transformation_matrix_path) 
        
        # Initialize mediapipe for hand tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False,  # False = video mode
                                         max_num_hands=1,
                                         min_detection_confidence=0.5,  # Minimum confidence for hand detection
                                         min_tracking_confidence=0.5)  # Minimum confidence for hand tracking
        self.mp_drawing = mp.solutions.drawing_utils

        self.frame = None  # To store the current frame
        self.results = None  # To store the hand detection results

    def update(self):
        """
        Capture a new frame from the camera and run hand detection.
        
        Returns:
        - True if a frame was successfully captured and processed, False otherwise.
        """
        ret, frame = self.cap.read()  # Capture a frame from the camera
        if not ret:
            print("Failed to capture frame")
            return False

        # Convert the frame color to RGB (mediapipe requires RGB images)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run hand detection on the RGB frame
        self.results = self.hands.process(rgb_frame)
        self.frame = frame  # Store the current frame
        return True

    def get_transformed_landmarks(self):
        """
        Get the hand landmarks transformed to the screen coordinates using the transformation matrix.
        
        Returns:
        - Transformed hand landmarks if available, None otherwise.
        """
        if self.results and self.results.multi_hand_landmarks:
            transformed_landmarks = []
            for hand_landmarks in self.results.multi_hand_landmarks:
                # Extract the coordinates of each landmark
                landmark_coords = []
                for landmark in hand_landmarks.landmark:
                    x = int(landmark.x * self.frame.shape[1])  # Convert x-coordinate to pixel value
                    y = int(landmark.y * self.frame.shape[0])  # Convert y-coordinate to pixel value
                    landmark_coords.append([x, y])
                
                landmark_coords = np.array(landmark_coords, dtype=np.float32)

                # Apply the transformation matrix to the landmark coordinates
                transformed_coords = cv2.perspectiveTransform(np.array([landmark_coords]), self.M)[0]
                
                # Clip the coordinates to ensure they are within the screen bounds
                transformed_coords = np.clip(transformed_coords, [0, 0], [self.width - 1, self.height - 1])
                transformed_landmarks.append(transformed_coords)

            return transformed_landmarks
        return None

    def release(self):
        """
        Release the camera and close all OpenCV windows.
        """
        self.cap.release()
        cv2.destroyAllWindows()
