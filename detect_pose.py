"""
Pose Detection Module
Uses MediaPipe to detect body landmarks in real-time
"""

import cv2
import mediapipe as mp
import numpy as np

class PoseDetector:
    def __init__(self, mode=False, complexity=1, smooth_landmarks=True):
        """
        Initialize pose detector
        
        Args:
            mode: Static/video mode (False = video, True = static)
            complexity: 0=fast, 1=accurate (higher = slower but better)
            smooth_landmarks: Smooth predictions across frames
        """
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=mode,
            model_complexity=complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def detect(self, frame):
        """
        Detect pose in frame
        
        Returns:
            frame: Annotated frame with landmarks
            landmarks: List of (x, y, z, visibility) for each body part
            success: Boolean if pose detected
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect pose
        results = self.pose.process(frame_rgb)
        
        h, w, c = frame.shape
        landmarks = []
        
        if results.pose_landmarks:
            # Extract landmarks
            for landmark in results.pose_landmarks.landmark:
                landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            
            # Draw landmarks on frame
            self.mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
            
            return frame, landmarks, True
        
        return frame, landmarks, False
    
    def get_landmark_by_name(self, landmarks, name):
        """
        Get specific landmark by name
        
        Available names:
        NOSE, LEFT_EYE, RIGHT_EYE, LEFT_EAR, RIGHT_EAR,
        LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW,
        LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP,
        LEFT_KNEE, RIGHT_KNEE, LEFT_ANKLE, RIGHT_ANKLE
        """
        landmark_names = {
            'NOSE': 0,
            'LEFT_EYE': 1, 'RIGHT_EYE': 2,
            'LEFT_EAR': 3, 'RIGHT_EAR': 4,
            'LEFT_SHOULDER': 11, 'RIGHT_SHOULDER': 12,
            'LEFT_ELBOW': 13, 'RIGHT_ELBOW': 14,
            'LEFT_WRIST': 15, 'RIGHT_WRIST': 16,
            'LEFT_HIP': 23, 'RIGHT_HIP': 24,
            'LEFT_KNEE': 25, 'RIGHT_KNEE': 26,
            'LEFT_ANKLE': 27, 'RIGHT_ANKLE': 28
        }
        
        idx = landmark_names.get(name)
        if idx is not None and idx < len(landmarks):
            return landmarks[idx]
        return None
    
    def close(self):
        """Clean up resources"""
        self.pose.close()
