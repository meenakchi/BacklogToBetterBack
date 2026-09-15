"""
Posture Calculator Module
Calculates angles and generates posture scores from landmarks
"""

import numpy as np
from scipy.spatial import distance

class PostureCalculator:
    
    @staticmethod
    def calculate_angle(point_a, point_b, point_c):
        """
        Calculate angle between three points (in degrees)
        
        Args:
            point_a, point_b, point_c: Dictionaries with 'x' and 'y' keys
        
        Returns:
            angle in degrees
        """
        # Vector from B to A
        vector_a = np.array([point_a['x'] - point_b['x'], point_a['y'] - point_b['y']])
        # Vector from B to C
        vector_c = np.array([point_c['x'] - point_b['x'], point_c['y'] - point_b['y']])
        
        # Calculate angle using dot product
        dot_product = np.dot(vector_a, vector_c)
        magnitude_a = np.linalg.norm(vector_a)
        magnitude_c = np.linalg.norm(vector_c)
        
        if magnitude_a == 0 or magnitude_c == 0:
            return 0
        
        cos_angle = dot_product / (magnitude_a * magnitude_c)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Handle floating point errors
        angle = np.arccos(cos_angle)
        
        return np.degrees(angle)
    
    @staticmethod
    def calculate_distance(point_a, point_b):
        """Calculate Euclidean distance between two points"""
        return distance.euclidean(
            [point_a['x'], point_a['y']],
            [point_b['x'], point_b['y']]
        )
    
    @staticmethod
    def get_posture_metrics(landmarks, detector):
        """
        Calculate posture metrics from landmarks
        
        Returns dictionary with:
        - neck_angle: Angle between shoulders and nose
        - left_shoulder_angle: Left arm angle
        - right_shoulder_angle: Right arm angle
        - shoulder_level: How level shoulders are (0 = level, higher = tilted)
        - spine_curvature: Forward head posture indicator
        """
        
        metrics = {}
        
        try:
            # Get key landmarks
            nose = detector.get_landmark_by_name(landmarks, 'NOSE')
            left_shoulder = detector.get_landmark_by_name(landmarks, 'LEFT_SHOULDER')
            right_shoulder = detector.get_landmark_by_name(landmarks, 'RIGHT_SHOULDER')
            left_ear = detector.get_landmark_by_name(landmarks, 'LEFT_EAR')
            right_ear = detector.get_landmark_by_name(landmarks, 'RIGHT_EAR')
            left_hip = detector.get_landmark_by_name(landmarks, 'LEFT_HIP')
            right_hip = detector.get_landmark_by_name(landmarks, 'RIGHT_HIP')
            
            if not all([nose, left_shoulder, right_shoulder, left_ear, right_ear]):
                return None
            
            # NECK ANGLE - angle between shoulders and nose
            # 180 degrees = perfectly straight, less = bent forward
            neck_angle = PostureCalculator.calculate_angle(nose, left_shoulder, right_shoulder)
            metrics['neck_angle'] = neck_angle
            
            # SHOULDER LEVEL - check if shoulders are tilted
            shoulder_diff = abs(left_shoulder['y'] - right_shoulder['y'])
            metrics['shoulder_level'] = shoulder_diff
            
            # FORWARD HEAD POSTURE - distance from nose to shoulder
            # If nose is too far forward, it's bad posture
            nose_shoulder_dist = PostureCalculator.calculate_distance(nose, left_shoulder)
            metrics['forward_head_posture'] = nose_shoulder_dist
            
            # BACK CURVATURE - if shoulders round forward
            left_ear_shoulder_angle = PostureCalculator.calculate_angle(
                left_ear, left_shoulder, left_hip
            )
            metrics['back_curvature'] = left_ear_shoulder_angle
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return None
    
    @staticmethod
    def calculate_posture_score(metrics):
        """
        Calculate overall posture score (0-100)
        
        100 = perfect posture
        0 = terrible posture
        """
        if metrics is None:
            return 0
        
        score = 100
        
        # NECK ANGLE (ideal: 160-180 degrees)
        neck_angle = metrics.get('neck_angle', 0)
        if neck_angle < 160:
            # Too bent forward
            score -= (160 - neck_angle) * 0.5
        elif neck_angle > 180:
            # Tilted back (less common)
            score -= (neck_angle - 180) * 0.3
        
        # SHOULDER LEVEL (ideal: very level, < 0.02)
        shoulder_level = metrics.get('shoulder_level', 0)
        if shoulder_level > 0.03:
            score -= shoulder_level * 500
        
        # FORWARD HEAD POSTURE (ideal: close to shoulder)
        fhp = metrics.get('forward_head_posture', 0)
        if fhp < 0.15:
            score -= (0.15 - fhp) * 200
        
        # BACK CURVATURE (ideal: 160-180 degrees)
        back_curve = metrics.get('back_curvature', 0)
        if back_curve < 160:
            score -= (160 - back_curve) * 0.3
        
        # Clamp score between 0-100
        return max(0, min(100, score))
    
    @staticmethod
    def get_posture_feedback(metrics, score):
        """Generate human-readable feedback"""
        feedback = []
        
        if score > 80:
            feedback.append("✅ Great posture! Keep it up!")
        elif score > 60:
            feedback.append("⚠️  Your posture is okay, but could be better")
        elif score > 40:
            feedback.append("❌ Your posture is slouching - sit up!")
        else:
            feedback.append("🚨 ALERT: Very bad posture - adjust immediately!")
        
        if metrics:
            neck_angle = metrics.get('neck_angle', 0)
            if neck_angle < 160:
                feedback.append(f"  • Neck bent forward (angle: {neck_angle:.1f}°)")
            
            shoulder_level = metrics.get('shoulder_level', 0)
            if shoulder_level > 0.03:
                feedback.append(f"  • Shoulders uneven/tilted")
            
            back_curve = metrics.get('back_curvature', 0)
            if back_curve < 160:
                feedback.append(f"  • Back is rounded/slouching")
        
        return "\n".join(feedback)
