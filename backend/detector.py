import cv2
import torch
import numpy as np
from ultralytics import YOLO
import time
import os
from datetime import datetime
import logging

class WeaponDetector:
    def __init__(self, model_path="yolov5s.pt", confidence_threshold=0.5):
        """
        Initialize the Weapon Detection System
        
        Args:
            model_path (str): Path to the trained YOLO model
            confidence_threshold (float): Minimum confidence for weapon detection
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load the YOLO model
        self.logger.info(f"Loading YOLO model from {model_path}")
        try:
            self.model = YOLO(model_path)
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            self.model = None
        
        # Detection history and statistics
        self.detection_history = []
        self.alert_history = []
        self.total_detections = 0
        self.total_alerts = 0
        self.alert_cooldown = 30  # seconds between alerts for same location
        self.last_alert_time = {}
        
        # Weapon classes to detect
        self.weapon_classes = ['knife', 'pistol', 'gun', 'rifle', 'sword', 'machete']
        
        self.logger.info("Weapon Detection System initialized successfully")
    
    def process_frame(self, frame):
        """
        Process a single frame for weapon detection
        
        Args:
            frame: OpenCV frame (numpy array)
            
        Returns:
            tuple: (processed_frame, detections, alert_triggered)
        """
        if self.model is None:
            self.logger.error("Model not loaded")
            return frame, [], False
            
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
                        
                        # Check if it's a weapon class
                        if class_name.lower() in self.weapon_classes:
                            detection = {
                                'class': class_name,
                                'confidence': float(confidence),
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'timestamp': datetime.now().isoformat()
                            }
                            detections.append(detection)
                            
                            # Draw bounding box
                            color = self._get_weapon_color(class_name)
                            cv2.rectangle(processed_frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                            
                            # Add label with confidence
                            label = f"{class_name}: {confidence:.2f}"
                            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                            
                            # Draw label background
                            cv2.rectangle(processed_frame, 
                                        (int(x1), int(y1) - label_size[1] - 10),
                                        (int(x1) + label_size[0], int(y1)),
                                        color, -1)
                            
                            # Draw label text
                            cv2.putText(processed_frame, label, (int(x1), int(y1) - 5), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                            
                            # Check if alert should be triggered
                            if self._should_trigger_alert(detection):
                                alert_triggered = True
                                self._trigger_alert(detection, processed_frame)
            
            # Add timestamp to frame
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(processed_frame, timestamp, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add detection count
            detection_text = f"Detections: {len(detections)}"
            cv2.putText(processed_frame, detection_text, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Update statistics
            self.total_detections += len(detections)
            if detections:
                self.detection_history.extend(detections)
            
            return processed_frame, detections, alert_triggered
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
            return frame, [], False
    
    def _get_weapon_color(self, class_name):
        """Get color for different weapon types"""
        color_map = {
            'pistol': (0, 0, 255),      # Red
            'gun': (0, 0, 255),         # Red
            'rifle': (0, 0, 255),       # Red
            'knife': (0, 255, 255),     # Yellow
            'sword': (0, 255, 255),     # Yellow
            'machete': (0, 255, 255),   # Yellow
        }
        return color_map.get(class_name.lower(), (0, 255, 0))  # Green default
    
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
        self.logger.warning(f"WEAPON ALERT: {detection['class']} detected with confidence {detection['confidence']:.2f}")
        
        # Create alerts directory if it doesn't exist
        alerts_dir = "alerts"
        os.makedirs(alerts_dir, exist_ok=True)
        
        # Save alert image
        alert_filename = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        alert_path = os.path.join(alerts_dir, alert_filename)
        cv2.imwrite(alert_path, frame)
        
        # Create alert record
        alert_record = {
            'id': len(self.alert_history) + 1,
            'detection': detection,
            'image_path': alert_path,
            'image_filename': alert_filename,
            'timestamp': datetime.now().isoformat(),
            'severity': 'high' if detection['confidence'] > 0.8 else 'medium'
        }
        
        # Store alert
        self.alert_history.append(alert_record)
        self.total_alerts += 1
        
        # Keep only last 100 alerts
        if len(self.alert_history) > 100:
            old_alert = self.alert_history.pop(0)
            # Remove old alert image file
            if os.path.exists(old_alert['image_path']):
                os.remove(old_alert['image_path'])
    
    def process_video_file(self, input_path, output_path):
        """
        Process a video file for weapon detection
        
        Args:
            input_path (str): Path to input video file
            output_path (str): Path to output video file
            
        Returns:
            dict: Summary of detections
        """
        self.logger.info(f"Processing video: {input_path}")
        
        # Open video file
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise Exception(f"Could not open video file: {input_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        total_detections = 0
        total_alerts = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                processed_frame, detections, alert_triggered = self.process_frame(frame)
                
                # Write processed frame
                out.write(processed_frame)
                
                # Update counters
                frame_count += 1
                total_detections += len(detections)
                if alert_triggered:
                    total_alerts += 1
                
                # Log progress every 100 frames
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    current_fps = frame_count / elapsed
                    self.logger.info(f"Processed {frame_count} frames at {current_fps:.2f} FPS")
        
        finally:
            cap.release()
            out.release()
        
        processing_time = time.time() - start_time
        avg_fps = frame_count / processing_time if processing_time > 0 else 0
        
        summary = {
            'total_frames': frame_count,
            'total_detections': total_detections,
            'total_alerts': total_alerts,
            'processing_time': processing_time,
            'average_fps': avg_fps,
            'output_file': output_path
        }
        
        self.logger.info(f"Video processing complete: {summary}")
        return summary
    
    def get_latest_alert(self):
        """Get the most recent alert"""
        if self.alert_history:
            return self.alert_history[-1]
        return None
    
    def get_alert_history(self, limit=50):
        """Get recent alert history"""
        return self.alert_history[-limit:] if self.alert_history else []
    
    def get_statistics(self):
        """Get detection statistics"""
        return {
            'total_detections': self.total_detections,
            'total_alerts': self.total_alerts,
            'recent_detections': len(self.detection_history),
            'recent_alerts': len(self.alert_history),
            'model_loaded': self.model is not None,
            'confidence_threshold': self.confidence_threshold,
            'weapon_classes': self.weapon_classes
        }
    
    def clear_history(self):
        """Clear detection and alert history"""
        self.detection_history.clear()
        self.alert_history.clear()
        self.total_detections = 0
        self.total_alerts = 0
        self.logger.info("History cleared")
