# Weapon Detection System

A comprehensive real-time weapon detection system built with YOLOv5, Flask API, and React frontend. This system can detect weapons like knives, pistols, rifles, and other dangerous objects using computer vision.

## 🚀 Features

- **Real-time Weapon Detection**: Uses YOLOv5 for accurate weapon detection
- **Multiple Input Sources**: Supports image upload, video files, webcam, and IP cameras
- **Web Dashboard**: Interactive React-based web interface
- **Live Webcam Detection**: Real-time weapon detection through webcam
- **Alert System**: Automatic alerts when weapons are detected
- **Statistics Tracking**: Comprehensive detection statistics and history
- **RESTful API**: Flask-based backend API for all operations
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Technology Stack

### Backend
- **Python 3.8+** with Flask
- **YOLOv5** for object detection
- **OpenCV** for video processing
- **Ultralytics** for model management

### Frontend
- **React 18** with Vite
- **Lucide React** for icons
- **Modern CSS** with responsive design

### System Components
- **Flask API Server** (Port 5000): Handles detection requests
- **Surveillance Server** (Port 8080): Web dashboard and monitoring
- **React Frontend** (Port 5173/5174): User interface

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Git
- Webcam (for live detection)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/VineetC137/Weapon-Detection_System.git
cd Weapon-Detection_System
```

### 2. Install Dependencies

#### Backend Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

### 3. Start the Servers

#### Option A: Start All Servers Automatically
```bash
# Run the installation script (Windows)
install.bat

# Or run setup script
python setup.py
```

#### Option B: Start Servers Manually

**Backend API Server:**
```bash
python backend/app.py
```

**Surveillance Server:**
```bash
python surveillance_server.py
```

**Frontend Development Server:**
```bash
cd frontend
npm run dev
```

### 4. Access the Application

- **Web Dashboard**: http://localhost:8080
- **React Frontend**: http://localhost:5173
- **API Health Check**: http://localhost:5000/health

## 📖 Usage Guide

### Image Upload Detection
1. Open the React frontend at http://localhost:5173
2. Click on "Image Upload" tab
3. Upload an image containing weapons
4. View detection results with bounding boxes and confidence scores

### Live Webcam Detection
1. Click on "Live Webcam" tab
2. Grant camera permissions when prompted
3. Click "Start Webcam" to begin real-time detection
4. Weapons will be detected and highlighted in real-time
5. Click "Stop Webcam" when finished

### Video File Processing
1. Use the surveillance server dashboard
2. Upload video files for batch processing
3. View processed videos with detection overlays

## 🔧 Configuration

### Detection Settings
- **Confidence Threshold**: Adjust in `backend/detector.py` (default: 0.5)
- **Alert Cooldown**: Set in `backend/detector.py` (default: 30 seconds)
- **Weapon Classes**: Configure in `backend/detector.py`

### Model Configuration
- **YOLO Model**: Uses `yolov5s.pt` by default
- **Custom Models**: Place in project root and update paths

## 📊 API Endpoints

### Health Check
- `GET /health` - Check system health and model status

### Image Detection
- `POST /detect-image` - Detect weapons in uploaded image

### Video Frame Detection
- `POST /detect/video` - Process single video frame from webcam

### Statistics
- `GET /stats` - Get detection statistics

### Alerts
- `GET /alerts` - Get detection alerts history

## 🎯 Detection Capabilities

The system can detect various weapons including:
- 🔫 Pistols and handguns
- 🔫 Rifles and long guns  
- 🔪 Knives and blades
- ⚔️ Swords and machetes
- 🗡️ Other sharp weapons

## 🚨 Alert System

- **Automatic Alerts**: Triggered when weapons are detected
- **Alert Images**: Saves snapshots of detection events
- **Alert History**: Maintains history of all alerts
- **Cooldown Period**: Prevents spam alerts (30 seconds)

## 📱 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   Flask API     │    │  YOLOv5 Model   │
│   (Port 5173)   │◄──►│  (Port 5000)    │◄──►│  (Detection)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Web Dashboard  │    │  Video/Frame    │    │  Alert System   │
│  (Port 8080)    │    │  Processing     │    │  & Statistics   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔒 Security Considerations

- **Privacy**: All processing is done locally
- **No External APIs**: No data sent to external services
- **Local Storage**: Images and videos stored locally
- **Access Control**: Implement authentication for production use

## 🐛 Troubleshooting

### Common Issues

**Camera Not Working:**
- Ensure camera permissions are granted
- Check if camera is being used by another application
- Try refreshing the page

**Model Loading Issues:**
- Verify `yolov5s.pt` file exists
- Check Python dependencies are installed
- Restart the backend server

**Frontend Build Issues:**
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version compatibility

**Port Conflicts:**
- Ensure ports 5000, 8080, and 5173 are available
- Modify ports in configuration files if needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- YOLOv5 by Ultralytics for the detection model
- Flask for the web framework
- React for the frontend framework
- OpenCV for computer vision capabilities

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**⭐ Star this repository if you find it helpful!**