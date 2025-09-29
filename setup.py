#!/usr/bin/env python3
"""
Setup script for Weapon Detection Surveillance System
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def check_model_file():
    """Check if YOLO model file exists"""
    if not os.path.exists("yolov5s.pt"):
        print("❌ Error: yolov5s.pt model file not found")
        print("Please ensure the YOLOv5 model file is in the project directory")
        return False
    print("✅ YOLO model file found")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["templates", "logs", "alerts", "videos"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")

def create_sample_config():
    """Create sample configuration files"""
    # Create notification config
    if not os.path.exists("notification_config.json"):
        from notification_system import create_notification_config
        create_notification_config()
        print("✅ Created sample notification configuration")

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        import torch
        import cv2
        import numpy as np
        from ultralytics import YOLO
        import flask
        import flask_socketio
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🛡️  WEAPON DETECTION SURVEILLANCE SYSTEM SETUP")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check model file
    if not check_model_file():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create sample configs
    create_sample_config()
    
    # Test imports
    if not test_imports():
        print("❌ Setup failed - some modules could not be imported")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n🚀 Quick Start:")
    print("1. Webcam detection: python run_surveillance.py --mode webcam")
    print("2. Web dashboard: python run_surveillance.py --mode web-server")
    print("3. IP cameras: python run_surveillance.py --mode ip-camera")
    print("\n📖 For more information, see README.md")
    print("=" * 60)

if __name__ == "__main__":
    main()
