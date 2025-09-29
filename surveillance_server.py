from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
import cv2
import base64
import threading
import time
import json
from datetime import datetime
import os
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
from weapon_detector import WeaponDetectionSystem
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'weapon_detection_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
detector = None
camera_thread = None
camera_running = False
current_frame = None
detection_stats = {
    'total_detections': 0,
    'knife_detections': 0,
    'pistol_detections': 0,
    'last_detection_time': None,
    'alerts_sent': 0
}

# Setup logging (terminal activities are not shown on frontend)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_detector():
    """Initialize the weapon detection system"""
    global detector
    try:
        detector = WeaponDetectionSystem(
            model_path="yolov5s.pt",
            confidence_threshold=0.5
        )
        
        # Add alert callback for real-time notifications
        detector.add_alert_callback(alert_callback)
        
        logger.info("Weapon detection system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize detector: {str(e)}")
        return False

def alert_callback(detection, frame, image_path):
    """Callback function for weapon detection alerts"""
    global detection_stats
    
    # Update statistics
    detection_stats['total_detections'] += 1
    detection_stats['last_detection_time'] = datetime.now().isoformat()
    detection_stats['alerts_sent'] += 1
    
    if detection['class'] == 'knife':
        detection_stats['knife_detections'] += 1
    elif detection['class'] == 'pistol':
        detection_stats['pistol_detections'] += 1
    
    # Send real-time alert to connected clients
    alert_data = {
        'type': 'weapon_detected',
        'detection': detection,
        'image_path': image_path,
        'timestamp': datetime.now().isoformat(),
        'stats': detection_stats
    }
    
    socketio.emit('weapon_alert', alert_data)
    logger.warning(f"WEAPON ALERT: {detection['class']} detected with confidence {detection['confidence']:.2f}")

def camera_worker():
    """Background thread for camera processing"""
    global camera_running, current_frame, detector
    
    if detector is None:
        logger.error("Detector not initialized")
        return
    
    # Try to open camera (0 for default webcam)
    logger.info("Attempting to open camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Could not open camera - please check if camera is connected and not being used by another application")
        return
    
    # Set camera properties for better performance and higher FPS
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size for lower latency
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))  # Use MJPEG for better performance
    
    camera_running = True
    logger.info("Camera started successfully")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while camera_running:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame from camera")
                continue
            
            frame_count += 1
            
            # Process frame for weapon detection
            processed_frame, detections, alert_triggered = detector.process_frame(frame)
            
            # Log detections (only to server logs, not frontend)
            if detections:
                for detection in detections:
                    logger.warning(f"WEAPON DETECTED: {detection['class']} with confidence {detection['confidence']:.2f}")
            
            # Encode frame for web display with optimized settings for better FPS
            _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            current_frame = frame_base64
            
            # Calculate current FPS
            current_fps = frame_count / (time.time() - start_time) if time.time() - start_time > 0 else 0
            
            # Send frame to connected clients for live webcam recording display
            socketio.emit('video_frame', {
                'frame': frame_base64,
                'detections': detections,
                'alert_triggered': alert_triggered,
                'timestamp': datetime.now().isoformat(),
                'fps': current_fps
            })
            
            # Log performance every 50 frames (server-side only)
            if frame_count % 50 == 0:
                logger.info(f"Processing at {current_fps:.2f} FPS - {frame_count} frames processed")
            
            # Optimized sleep for better FPS - reduced from 33ms to 16ms for ~60 FPS
            time.sleep(0.016)  # ~60 FPS
    
    except Exception as e:
        logger.error(f"Error in camera worker: {str(e)}")
    
    finally:
        cap.release()
        camera_running = False
        logger.info("Camera stopped")

@app.route('/')
def index():
    """Main surveillance dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get current detection statistics"""
    return jsonify(detection_stats)

@app.route('/api/history')
def get_detection_history():
    """Get detection history"""
    if detector:
        return jsonify(detector.get_detection_history())
    return jsonify([])

@app.route('/api/start_camera', methods=['POST'])
def start_camera():
    """Start camera processing"""
    global camera_thread, camera_running
    
    if camera_running:
        return jsonify({'status': 'already_running'})
    
    if detector is None:
        return jsonify({'status': 'error', 'message': 'Detector not initialized'})
    
    camera_thread = threading.Thread(target=camera_worker)
    camera_thread.daemon = True
    camera_thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/api/stop_camera', methods=['POST'])
def stop_camera():
    """Stop camera processing"""
    global camera_running
    
    camera_running = False
    return jsonify({'status': 'stopped'})

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    """Clear detection history"""
    if detector:
        detector.clear_detection_history()
        global detection_stats
        detection_stats = {
            'total_detections': 0,
            'knife_detections': 0,
            'pistol_detections': 0,
            'last_detection_time': None,
            'alerts_sent': 0
        }
        return jsonify({'status': 'cleared'})
    return jsonify({'status': 'error', 'message': 'Detector not initialized'})

@app.route('/api/alert_image/<filename>')
def get_alert_image(filename):
    """Serve alert images"""
    try:
        # Check if file exists in current directory or alerts directory
        file_path = filename
        if not os.path.exists(file_path):
            file_path = os.path.join('alerts', filename)
        
        if os.path.exists(file_path):
            return Response(open(file_path, 'rb').read(), mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        logger.error(f"Error serving alert image: {str(e)}")
        return jsonify({'error': 'Error serving image'}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to surveillance system'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('request_frame')
def handle_frame_request():
    """Handle frame request from client"""
    if current_frame:
        emit('video_frame', {
            'frame': current_frame,
            'timestamp': datetime.now().isoformat()
        })

# Removed terminal log handlers - terminal activities are no longer shown on frontend

if __name__ == '__main__':
    # Initialize the weapon detection system
    if not initialize_detector():
        logger.error("Failed to initialize weapon detection system")
        exit(1)
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Start the Flask-SocketIO server
    logger.info("Starting surveillance server on http://localhost:8080")
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
