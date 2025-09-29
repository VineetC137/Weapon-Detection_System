from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import base64
import os
import tempfile
from datetime import datetime
import json
from detector import WeaponDetector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the weapon detector
detector = WeaponDetector()

# Create necessary directories
os.makedirs('alerts', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('processed', exist_ok=True)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': detector.model is not None
    })

@app.route('/detect-image', methods=['POST'])
def detect_image():
    """
    Detect weapons in an image frame
    Expected input: JSON with 'image' field containing base64 encoded image
    Returns: JSON with detections and processed image
    """
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image'].split(',')[1] if ',' in data['image'] else data['image']
        image_bytes = base64.b64decode(image_data)
        
        # Convert to OpenCV format
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Process frame for weapon detection
        processed_frame, detections, alert_triggered = detector.process_frame(frame)
        
        # Encode processed frame back to base64
        _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        processed_image = base64.b64encode(buffer).decode('utf-8')
        
        # Prepare response
        response = {
            'detections': detections,
            'alert_triggered': alert_triggered,
            'processed_image': f"data:image/jpeg;base64,{processed_image}",
            'timestamp': datetime.now().isoformat(),
            'frame_count': len(detections)
        }
        
        # Add alert image path if alert was triggered
        if alert_triggered and detections:
            latest_alert = detector.get_latest_alert()
            if latest_alert:
                response['alert_image'] = latest_alert['image_path']
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in detect-image endpoint: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/upload-video', methods=['POST'])
def upload_video():
    """
    Process uploaded video file for weapon detection
    Expected input: Multipart form data with 'video' file
    Returns: JSON with download link to processed video
    """
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        allowed_extensions = {'mp4', 'avi', 'mov', 'mkv', 'wmv'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'Unsupported file format. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        # Save uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        input_filename = f"input_{timestamp}.{file_ext}"
        input_path = os.path.join('uploads', input_filename)
        file.save(input_path)
        
        # Process video
        output_filename = f"processed_{timestamp}.mp4"
        output_path = os.path.join('processed', output_filename)
        
        logger.info(f"Processing video: {input_path} -> {output_path}")
        detections_summary = detector.process_video_file(input_path, output_path)
        
        # Clean up input file
        os.remove(input_path)
        
        return jsonify({
            'status': 'success',
            'processed_video': f'/download/{output_filename}',
            'detections_summary': detections_summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in upload-video endpoint: {str(e)}")
        return jsonify({'error': f'Video processing failed: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed video file"""
    try:
        file_path = os.path.join('processed', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/alerts', methods=['GET'])
def get_alerts():
    """Get list of recent alerts"""
    try:
        alerts = detector.get_alert_history()
        return jsonify({
            'alerts': alerts,
            'count': len(alerts)
        })
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        return jsonify({'error': 'Failed to retrieve alerts'}), 500

@app.route('/alerts/<filename>')
def get_alert_image(filename):
    """Serve alert images"""
    try:
        file_path = os.path.join('alerts', filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': 'Alert image not found'}), 404
    except Exception as e:
        logger.error(f"Error serving alert image: {str(e)}")
        return jsonify({'error': 'Failed to serve image'}), 500

@app.route('/detect/video', methods=['POST'])
def detect_video_frame():
    """
    Detect weapons in a single video frame from webcam
    Expected input: JSON with 'frame' field containing base64 encoded image
    Returns: JSON with detections
    """
    try:
        data = request.get_json()
        if not data or 'frame' not in data:
            return jsonify({'error': 'No frame data provided'}), 400
        
        # Decode base64 image
        frame_data = data['frame'].split(',')[1] if ',' in data['frame'] else data['frame']
        image_bytes = base64.b64decode(frame_data)
        
        # Convert to OpenCV format
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid frame format'}), 400
        
        # Process frame for weapon detection
        processed_frame, detections, alert_triggered = detector.process_frame(frame)
        
        # Convert detections to the format expected by frontend
        formatted_detections = []
        for detection in detections:
            formatted_detections.append({
                'class': detection['class'],
                'confidence': detection['confidence'],
                'bbox': detection['bbox'],  # [x1, y1, x2, y2]
                'timestamp': datetime.now().isoformat()
            })
        
        # Prepare response
        response = {
            'detections': formatted_detections,
            'alert_triggered': alert_triggered,
            'timestamp': datetime.now().isoformat(),
            'frame_processed': True
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in detect-video-frame endpoint: {str(e)}")
        return jsonify({'error': f'Frame processing failed: {str(e)}'}), 500
def get_stats():
    """Get detection statistics"""
    try:
        stats = detector.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

if __name__ == '__main__':
    logger.info("Starting Weapon Detection API Server...")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /detect-image - Detect weapons in image")
    logger.info("  POST /upload-video - Process video file")
    logger.info("  GET  /alerts - Get alert history")
    logger.info("  GET  /stats - Get detection statistics")
    logger.info("  GET  /download/<filename> - Download processed video")
    logger.info("  GET  /alerts/<filename> - Get alert image")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
