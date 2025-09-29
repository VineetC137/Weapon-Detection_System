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
import requests
import logging
from weapon_detector import WeaponDetectionSystem

class IPCameraWeaponDetector:
    def __init__(self, model_path="yolov5s.pt", confidence_threshold=0.5):
        """
        Initialize IP Camera Weapon Detection System
        
        Args:
            model_path (str): Path to the trained YOLO model
            confidence_threshold (float): Minimum confidence for weapon detection
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Load the YOLO model
        self.logger.info(f"Loading YOLO model from {model_path}")
        self.model = YOLO(model_path)
        
        # Detection history
        self.detection_history = []
        self.alert_cooldown = 30  # seconds between alerts
        self.last_alert_time = {}
        
        # Camera configurations
        self.cameras = {}
        self.camera_threads = {}
        self.camera_running = {}
        
        # Alert system
        self.alert_callbacks = []
        
        self.logger.info("IP Camera Weapon Detection System initialized successfully")
    
    def add_camera(self, camera_id, camera_url, camera_name="Camera"):
        """
        Add an IP camera to the surveillance system
        
        Args:
            camera_id (str): Unique identifier for the camera
            camera_url (str): RTSP/HTTP URL of the camera
            camera_name (str): Display name for the camera
        """
        self.cameras[camera_id] = {
            'url': camera_url,
            'name': camera_name,
            'last_detection': None,
            'detection_count': 0
        }
        self.logger.info(f"Added camera {camera_id}: {camera_name} at {camera_url}")
    
    def add_alert_callback(self, callback):
        """Add a callback function to be called when weapons are detected"""
        self.alert_callbacks.append(callback)
    
    def _should_trigger_alert(self, detection, camera_id):
        """Check if an alert should be triggered based on cooldown and location"""
        current_time = time.time()
        location_key = f"{camera_id}_{detection['class']}_{detection['bbox'][0]}_{detection['bbox'][1]}"
        
        if location_key in self.last_alert_time:
            if current_time - self.last_alert_time[location_key] < self.alert_cooldown:
                return False
        
        self.last_alert_time[location_key] = current_time
        return True
    
    def _trigger_alert(self, detection, frame, camera_id, alert_image_path):
        """Trigger alert for weapon detection"""
        camera_name = self.cameras[camera_id]['name']
        self.logger.warning(f"WEAPON DETECTED on {camera_name}: {detection['class']} with confidence {detection['confidence']:.2f}")
        
        # Update camera detection count
        self.cameras[camera_id]['detection_count'] += 1
        self.cameras[camera_id]['last_detection'] = datetime.now().isoformat()
        
        # Store detection in history
        self.detection_history.append({
            'camera_id': camera_id,
            'camera_name': camera_name,
            'detection': detection,
            'image_path': alert_image_path,
            'timestamp': datetime.now().isoformat()
        })
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(detection, frame, camera_id, camera_name, alert_image_path)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {str(e)}")
    
    def _process_camera_stream(self, camera_id):
        """Process video stream from a specific camera"""
        camera_info = self.cameras[camera_id]
        camera_url = camera_info['url']
        camera_name = camera_info['name']
        
        self.logger.info(f"Starting stream processing for {camera_name} ({camera_id})")
        
        # Open camera stream
        cap = cv2.VideoCapture(camera_url)
        if not cap.isOpened():
            self.logger.error(f"Could not open camera stream: {camera_url}")
            return
        
        # Set buffer size to reduce latency
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while self.camera_running.get(camera_id, False):
                ret, frame = cap.read()
                if not ret:
                    self.logger.warning(f"Failed to read frame from {camera_name}")
                    time.sleep(0.1)
                    continue
                
                # Process frame for weapon detection
                results = self.model(frame, conf=self.confidence_threshold)
                
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
                                color = (0, 0, 255) if class_name == 'pistol' else (0, 255, 255)
                                cv2.rectangle(processed_frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                                
                                # Add label
                                label = f"{class_name}: {confidence:.2f}"
                                cv2.putText(processed_frame, label, (int(x1), int(y1)-10), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                                
                                # Check if alert should be triggered
                                if self._should_trigger_alert(detection, camera_id):
                                    alert_triggered = True
                                    alert_filename = f"alert_{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                                    cv2.imwrite(alert_filename, processed_frame)
                                    self._trigger_alert(detection, processed_frame, camera_id, alert_filename)
                
                # Add camera info and timestamp to frame
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(processed_frame, f"{camera_name} - {timestamp}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Add detection count
                detection_count = self.cameras[camera_id]['detection_count']
                cv2.putText(processed_frame, f"Detections: {detection_count}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                frame_count += 1
                
                # Log performance every 100 frames
                if frame_count % 100 == 0:
                    elapsed_time = time.time() - start_time
                    current_fps = frame_count / elapsed_time
                    self.logger.info(f"{camera_name}: Processed {frame_count} frames at {current_fps:.2f} FPS")
        
        except Exception as e:
            self.logger.error(f"Error processing {camera_name}: {str(e)}")
        
        finally:
            cap.release()
            self.camera_running[camera_id] = False
            self.logger.info(f"Stopped processing {camera_name}")
    
    def start_camera(self, camera_id):
        """Start processing a specific camera"""
        if camera_id not in self.cameras:
            self.logger.error(f"Camera {camera_id} not found")
            return False
        
        if self.camera_running.get(camera_id, False):
            self.logger.warning(f"Camera {camera_id} is already running")
            return False
        
        self.camera_running[camera_id] = True
        thread = threading.Thread(target=self._process_camera_stream, args=(camera_id,))
        thread.daemon = True
        thread.start()
        self.camera_threads[camera_id] = thread
        
        self.logger.info(f"Started camera {camera_id}")
        return True
    
    def stop_camera(self, camera_id):
        """Stop processing a specific camera"""
        if camera_id not in self.cameras:
            self.logger.error(f"Camera {camera_id} not found")
            return False
        
        self.camera_running[camera_id] = False
        if camera_id in self.camera_threads:
            self.camera_threads[camera_id].join(timeout=5)
            del self.camera_threads[camera_id]
        
        self.logger.info(f"Stopped camera {camera_id}")
        return True
    
    def start_all_cameras(self):
        """Start processing all cameras"""
        for camera_id in self.cameras:
            self.start_camera(camera_id)
    
    def stop_all_cameras(self):
        """Stop processing all cameras"""
        for camera_id in list(self.camera_running.keys()):
            self.stop_camera(camera_id)
    
    def get_camera_status(self):
        """Get status of all cameras"""
        status = {}
        for camera_id, camera_info in self.cameras.items():
            status[camera_id] = {
                'name': camera_info['name'],
                'url': camera_info['url'],
                'running': self.camera_running.get(camera_id, False),
                'detection_count': camera_info['detection_count'],
                'last_detection': camera_info['last_detection']
            }
        return status
    
    def get_detection_history(self):
        """Get the detection history"""
        return self.detection_history
    
    def clear_detection_history(self):
        """Clear the detection history"""
        self.detection_history.clear()
        for camera_id in self.cameras:
            self.cameras[camera_id]['detection_count'] = 0
            self.cameras[camera_id]['last_detection'] = None
        self.logger.info("Detection history cleared")

def email_alert_callback(detection, frame, camera_id, camera_name, image_path):
    """Example email alert callback for IP cameras"""
    print(f"EMAIL ALERT: {detection['class']} detected on {camera_name} ({camera_id})")
    print(f"Confidence: {detection['confidence']:.2f}")
    print(f"Alert image saved as: {image_path}")
    # Implement email sending logic here

def console_alert_callback(detection, frame, camera_id, camera_name, image_path):
    """Example console alert callback for IP cameras"""
    print(f"CONSOLE ALERT: {detection['class']} detected on {camera_name} ({camera_id})")
    print(f"Confidence: {detection['confidence']:.2f}")
    print(f"Alert image saved as: {image_path}")

if __name__ == "__main__":
    # Initialize the IP camera weapon detection system
    detector = IPCameraWeaponDetector(
        model_path="yolov5s.pt",
        confidence_threshold=0.5
    )
    
    # Add alert callbacks
    detector.add_alert_callback(console_alert_callback)
    # detector.add_alert_callback(email_alert_callback)  # Uncomment to enable email alerts
    
    # Example: Add IP cameras
    # Replace with your actual camera URLs
    detector.add_camera("cam1", "rtsp://username:password@192.168.1.100:554/stream", "Main Entrance")
    detector.add_camera("cam2", "rtsp://username:password@192.168.1.101:554/stream", "Parking Lot")
    detector.add_camera("cam3", "http://192.168.1.102:8080/video", "Reception Area")
    
    # Start all cameras
    detector.start_all_cameras()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
            # Print status every 30 seconds
            if int(time.time()) % 30 == 0:
                status = detector.get_camera_status()
                print("\n=== Camera Status ===")
                for camera_id, info in status.items():
                    print(f"{info['name']} ({camera_id}): {'Running' if info['running'] else 'Stopped'} - {info['detection_count']} detections")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        detector.stop_all_cameras()
        print("All cameras stopped.")
