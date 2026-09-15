"""
Posture Monitor - Main Application
Real-time posture detection and monitoring

Usage:
    python main.py
    
Controls:
    'q' - Quit
    's' - Save screenshot
    'r' - Reset posture alerts
"""

import cv2
import time
from datetime import datetime
import os
from detect_pose import PoseDetector
from posture_calculator import PostureCalculator
from database import PostureDatabase

class PostureMonitor:
    def __init__(self):
        """Initialize posture monitor"""
        self.detector = PoseDetector(complexity=1)
        self.calculator = PostureCalculator()
        self.db = PostureDatabase()
        
        # Monitoring settings
        self.alert_threshold = 60  # Score below this triggers alert
        self.alert_cooldown = 2  # Seconds between alerts
        self.last_alert_time = 0
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.fps = 0
        
        # Session tracking
        self.session_id = None
        self.session_start = None
        
    def start_session(self):
        """Start monitoring session"""
        self.session_id = self.db.start_session()
        self.session_start = time.time()
        print(f"\n🎯 Session started (ID: {self.session_id})")
    
    def end_session(self):
        """End monitoring session"""
        if self.session_id:
            stats = self.db.end_session(self.session_id)
            duration_min = stats['duration'] / 60
            print(f"\n📊 Session ended!")
            print(f"  Duration: {duration_min:.1f} minutes")
            print(f"  Avg Score: {stats['avg_score']:.1f}")
            print(f"  Min Score: {stats['min_score']:.1f}")
            print(f"  Max Score: {stats['max_score']:.1f}")
    
    def trigger_alert(self, score):
        """Trigger posture alert"""
        current_time = time.time()
        
        # Cooldown check (don't spam alerts)
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
        
        self.last_alert_time = current_time
        
        # Visual + audio alert
        print(f"\n🚨 POSTURE ALERT! Score: {score:.1f}")
        
        # Try beep (works on most systems)
        try:
            for _ in range(3):
                print('\a', end='', flush=True)
                time.sleep(0.1)
        except:
            pass
        
        # Record alert in database
        if self.session_id:
            self.db.record_alert(self.session_id)
    
    def process_frame(self, frame):
        """Process single frame"""
        # Detect pose
        frame, landmarks, success = self.detector.detect(frame)
        
        posture_score = 0
        feedback = "Detecting..."
        
        if success and len(landmarks) > 0:
            # Calculate posture metrics
            metrics = self.calculator.get_posture_metrics(landmarks, self.detector)
            
            if metrics:
                posture_score = self.calculator.calculate_posture_score(metrics)
                feedback = self.calculator.get_posture_feedback(metrics, posture_score)
                
                # Record to database
                if self.session_id:
                    self.db.record_frame(self.session_id, posture_score, metrics)
                
                # Check for alert
                if posture_score < self.alert_threshold:
                    self.trigger_alert(posture_score)
        
        return frame, posture_score, feedback
    
    def draw_hud(self, frame, score, feedback):
        """Draw heads-up display on frame"""
        h, w, _ = frame.shape
        
        # Background box for score
        score_color = (0, 255, 0) if score > 70 else (0, 165, 255) if score > 50 else (0, 0, 255)
        
        cv2.rectangle(frame, (10, 10), (250, 100), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (250, 100), score_color, 2)
        
        # Posture score
        cv2.putText(frame, f"Posture Score: {score:.1f}", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, score_color, 2)
        cv2.putText(frame, f"Threshold: {self.alert_threshold}", (20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (w - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Feedback
        feedback_box_y = 120
        cv2.rectangle(frame, (10, feedback_box_y), (w-10, feedback_box_y + 80), (0, 0, 0), -1)
        
        y_offset = feedback_box_y + 20
        for line in feedback.split('\n'):
            cv2.putText(frame, line, (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_offset += 25
        
        # Instructions
        cv2.putText(frame, "Press 'q' to quit | 's' to save", (10, h-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def update_fps(self):
        """Calculate FPS"""
        self.frame_count += 1
        elapsed = time.time() - self.fps_start_time
        
        if elapsed >= 1:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_start_time = time.time()
    
    def run(self, camera_id=0):
        """Main monitoring loop"""
        print("""
╔════════════════════════════════════════╗
║     🧘 POSTURE MONITOR v1.0 🧘        ║
║  Real-time Posture Detection & Alerts ║
╚════════════════════════════════════════╝
        """)
        
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        print("✅ Camera opened")
        print("Starting session...")
        self.start_session()
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("❌ Error reading frame")
                    break
                
                # Flip for selfie view
                frame = cv2.flip(frame, 1)
                
                # Process frame
                frame, score, feedback = self.process_frame(frame)
                
                # Update FPS
                self.update_fps()
                
                # Draw HUD
                frame = self.draw_hud(frame, score, feedback)
                
                # Display
                cv2.imshow('Posture Monitor', frame)
                
                # Keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):  # Quit
                    break
                elif key == ord('s'):  # Save screenshot
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"posture_snapshot_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"📸 Saved: {filename}")
                elif key == ord('r'):  # Reset alerts
                    self.last_alert_time = 0
                    print("🔄 Alert cooldown reset")
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        
        finally:
            print("\nClosing session...")
            self.end_session()
            cap.release()
            cv2.destroyAllWindows()
            self.detector.close()

def main():
    """Entry point"""
    monitor = PostureMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
