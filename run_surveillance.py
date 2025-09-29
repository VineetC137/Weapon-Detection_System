#!/usr/bin/env python3
"""
Main script to run the Weapon Detection Surveillance System
Supports both webcam and IP camera monitoring with real-time notifications
"""

import argparse
import sys
import os
import logging
from datetime import datetime
import signal
import time

# Import our modules
from weapon_detector import WeaponDetectionSystem
from ip_camera_detector import IPCameraWeaponDetector
from surveillance_server import app, socketio, initialize_detector
from notification_system import NotificationSystem

def setup_logging(log_level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'surveillance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print('\nShutting down surveillance system...')
    sys.exit(0)

def run_webcam_detection(confidence_threshold=0.5, display=True, save_video=False):
    """Run weapon detection on webcam"""
    print("Starting webcam weapon detection...")
    
    # Initialize detector
    detector = WeaponDetectionSystem(
        model_path="yolov5s.pt",
        confidence_threshold=confidence_threshold
    )
    
    # Add console alert callback
    detector.add_alert_callback(lambda detection, frame, image_path: 
        print(f"ALERT: {detection['class']} detected with confidence {detection['confidence']:.2f}"))
    
    # Start processing
    detector.process_video_stream(
        source=0,  # Default webcam
        display=display,
        save_video=save_video,
        output_path=f"surveillance_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    )

def run_ip_camera_detection(camera_configs, confidence_threshold=0.5):
    """Run weapon detection on IP cameras"""
    print("Starting IP camera weapon detection...")
    
    # Initialize detector
    detector = IPCameraWeaponDetector(
        model_path="yolov5s.pt",
        confidence_threshold=confidence_threshold
    )
    
    # Add cameras
    for config in camera_configs:
        detector.add_camera(
            camera_id=config['id'],
            camera_url=config['url'],
            camera_name=config['name']
        )
    
    # Add console alert callback
    detector.add_alert_callback(lambda detection, frame, camera_id, camera_name, image_path: 
        print(f"ALERT: {detection['class']} detected on {camera_name} with confidence {detection['confidence']:.2f}"))
    
    # Start all cameras
    detector.start_all_cameras()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping IP camera detection...")
        detector.stop_all_cameras()

def run_web_server(host='0.0.0.0', port=5000, debug=False):
    """Run the web-based surveillance server"""
    print(f"Starting web surveillance server on http://{host}:{port}")
    
    # Initialize detector
    if not initialize_detector():
        print("Failed to initialize weapon detection system")
        return
    
    # Start the server
    socketio.run(app, host=host, port=port, debug=debug)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Weapon Detection Surveillance System')
    parser.add_argument('--mode', choices=['webcam', 'ip-camera', 'web-server'], 
                       default='webcam', help='Detection mode')
    parser.add_argument('--confidence', type=float, default=0.5, 
                       help='Confidence threshold for detection (0.0-1.0)')
    parser.add_argument('--no-display', action='store_true', 
                       help='Disable video display (for webcam mode)')
    parser.add_argument('--save-video', action='store_true', 
                       help='Save processed video (for webcam mode)')
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Host for web server mode')
    parser.add_argument('--port', type=int, default=5000, 
                       help='Port for web server mode')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(getattr(logging, args.log_level))
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("🛡️  WEAPON DETECTION SURVEILLANCE SYSTEM")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Confidence Threshold: {args.confidence}")
    print(f"Log Level: {args.log_level}")
    print("=" * 60)
    
    try:
        if args.mode == 'webcam':
            run_webcam_detection(
                confidence_threshold=args.confidence,
                display=not args.no_display,
                save_video=args.save_video
            )
        
        elif args.mode == 'ip-camera':
            # Example IP camera configurations
            # Replace with your actual camera URLs
            camera_configs = [
                {
                    'id': 'cam1',
                    'url': 'rtsp://username:password@192.168.1.100:554/stream',
                    'name': 'Main Entrance'
                },
                {
                    'id': 'cam2', 
                    'url': 'rtsp://username:password@192.168.1.101:554/stream',
                    'name': 'Parking Lot'
                },
                {
                    'id': 'cam3',
                    'url': 'http://192.168.1.102:8080/video',
                    'name': 'Reception Area'
                }
            ]
            
            run_ip_camera_detection(
                camera_configs=camera_configs,
                confidence_threshold=args.confidence
            )
        
        elif args.mode == 'web-server':
            run_web_server(
                host=args.host,
                port=args.port,
                debug=args.debug
            )
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
