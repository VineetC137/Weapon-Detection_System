import cv2
import torch
import numpy as np
from ultralytics import YOLO
import time
import json
from datetime import datetime
import os
import threading
import queue
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import logging

class WeaponDetectionSystem:
    def __init__(self, model_path="yolov5s.pt", confidence_threshold=0.5, notification_email=None):
        """
        Initialize the Weapon Detection System
        
        Args:
            model_path (str): Path to the trained YOLO model
            confidence_threshold (float): Minimum confidence for weapon detection
            notification_email (str): Email for security notifications
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.notification_email = notification_email
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Load the YOLO model
        self.logger.info(f"Loading YOLO model from {model_path}")
        self.model = YOLO(model_path)
        
        # Detection history for tracking
        self.detection_history = []
        self.alert_cooldown = 30  # seconds between alerts for same location
        self.last_alert_time = {}
        
        # Video processing queue
        self.frame_queue = queue.Queue(maxsize=10)
        self.result_queue = queue.Queue()
        
        # Alert system
        self.alert_callbacks = []
        
        self.logger.info("Weapon Detection System initialized successfully")
    
    def add_alert_callback(self, callback):
        """Add a callback function to be called when weapons are detected"""
        self.alert_callbacks.append(callback)
    
    def process_frame(self, frame):
        """
        Process a single frame for weapon detection
        
        Args:
            frame: OpenCV frame (numpy array)
            
        Returns:
            tuple: (processed_frame, detections, alert_triggered)
        """
        try:
            # Run YOLO detection
            results = self.model(frame, conf=self.confidence_threshold)
            
            # Process results
            detections = []
            alert_triggered = False
            processed_frame = frame.copy()
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract box coordinates and confidence
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.model.names[class_id]
                        
                        # Only process weapon classes (knife, pistol)
                        if class_name in ['knife', 'pistol']:
                            detection = {
                                'class': class_name,
                                'confidence': float(confidence),
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'timestamp': datetime.now().isoformat()
                            }
                            detections.append(detection)
                            
                            # Draw bounding box
                            color = (0, 0, 255) if class_name == 'pistol' else (0, 255, 255)  # Red for pistol, Yellow for knife
                            cv2.rectangle(processed_frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                            
                            # Add label
                            label = f"{class_name}: {confidence:.2f}"
                            cv2.putText(processed_frame, label, (int(x1), int(y1)-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                            
                            # Check if alert should be triggered
                            if self._should_trigger_alert(detection):
                                alert_triggered = True
                                self._trigger_alert(detection, processed_frame)
            
            # Add timestamp to frame
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(processed_frame, timestamp, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            return processed_frame, detections, alert_triggered
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
            return frame, [], False
    
    def _should_trigger_alert(self, detection):
        """Check if an alert should be triggered based on cooldown and location"""
        current_time = time.time()
        location_key = f"{detection['class']}_{detection['bbox'][0]}_{detection['bbox'][1]}"
        
        if location_key in self.last_alert_time:
            if current_time - self.last_alert_time[location_key] < self.alert_cooldown:
                return False
        
        self.last_alert_time[location_key] = current_time
        return True
    
    def _trigger_alert(self, detection, frame):
        """Trigger alert for weapon detection"""
        self.logger.warning(f"WEAPON DETECTED: {detection['class']} with confidence {detection['confidence']:.2f}")
        
        # Create alerts directory if it doesn't exist
        alerts_dir = "alerts"
        os.makedirs(alerts_dir, exist_ok=True)
        
        # Save alert image in alerts directory
        alert_filename = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        alert_path = os.path.join(alerts_dir, alert_filename)
        cv2.imwrite(alert_path, frame)
        
        # Store detection in history
        self.detection_history.append({
            'detection': detection,
            'image_path': alert_path,
            'timestamp': datetime.now().isoformat()
        })
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(detection, frame, alert_path)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {str(e)}")
    
    def process_video_stream(self, source=0, display=True, save_video=False, output_path="output.avi"):
        """
        Process video stream from camera or video file
        
        Args:
            source: Camera index (0 for default webcam) or video file path
            display: Whether to display the video
            save_video: Whether to save the processed video
            output_path: Path to save the output video
        """
        self.logger.info(f"Starting video stream from source: {source}")
        
        # Open video source
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            self.logger.error(f"Error: Could not open video source {source}")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.logger.info(f"Video properties: {width}x{height} @ {fps} FPS")
        
        # Setup video writer if saving
        writer = None
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    self.logger.warning("End of video stream")
                    break
                
                # Process frame
                processed_frame, detections, alert_triggered = self.process_frame(frame)
                
                # Add status information
                status_text = f"Detections: {len(detections)} | Alerts: {'YES' if alert_triggered else 'NO'}"
                cv2.putText(processed_frame, status_text, (10, height - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Save frame if writing video
                if writer is not None:
                    writer.write(processed_frame)
                
                # Display frame
                if display:
                    cv2.imshow('Weapon Detection System', processed_frame)
                    
                    # Check for exit key
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:  # 'q' or ESC
                        self.logger.info("User requested exit")
                        break
                
                frame_count += 1
                
                # Log performance every 100 frames
                if frame_count % 100 == 0:
                    elapsed_time = time.time() - start_time
                    current_fps = frame_count / elapsed_time
                    self.logger.info(f"Processed {frame_count} frames at {current_fps:.2f} FPS")
        
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        
        finally:
            # Cleanup
            cap.release()
            if writer is not None:
                writer.release()
            cv2.destroyAllWindows()
            
            # Log final statistics
            total_time = time.time() - start_time
            avg_fps = frame_count / total_time if total_time > 0 else 0
            self.logger.info(f"Processing complete. Total frames: {frame_count}, Average FPS: {avg_fps:.2f}")
    
    def get_detection_history(self):
        """Get the detection history"""
        return self.detection_history
    
    def clear_detection_history(self):
        """Clear the detection history"""
        self.detection_history.clear()
        self.logger.info("Detection history cleared")

def email_alert_callback(detection, frame, image_path):
    """Example email alert callback"""
    print(f"Email alert: {detection['class']} detected with confidence {detection['confidence']:.2f}")
    # Implement email sending logic here

def console_alert_callback(detection, frame, image_path):
    """Example console alert callback"""
    print(f"CONSOLE ALERT: {detection['class']} detected with confidence {detection['confidence']:.2f}")
    print(f"Alert image saved as: {image_path}")

if __name__ == "__main__":
    # Initialize the weapon detection system
    detector = WeaponDetectionSystem(
        model_path="yolov5s.pt",
        confidence_threshold=0.5
    )
    
    # Add alert callbacks
    detector.add_alert_callback(console_alert_callback)
    # detector.add_alert_callback(email_alert_callback)  # Uncomment to enable email alerts
    
    # Start processing video stream
    # Use 0 for default webcam, or provide path to video file
    detector.process_video_stream(source=0, display=True, save_video=False)
