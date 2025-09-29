# 🛡️ Weapon Detection Surveillance System

A real-time weapon identification system using YOLOv5 for surveillance video cameras and smart IP cameras with real-time notifications to security staff.

## 🎯 Problem Statement

To identify potential instances of violence and deter criminal activities, this system provides real-time weapon identification in surveillance video using deep learning. It can identify weapons in surveillance video cameras or smart IP cameras and give real-time notifications to security staff.

## ✨ Features

- **Real-time Weapon Detection**: Identifies knives and pistols in live video streams
- **Multiple Camera Support**: Works with webcams and IP cameras (RTSP/HTTP)
- **Web-based Dashboard**: Modern, responsive interface for security staff
- **Real-time Notifications**: Instant alerts via email, SMS, and webhooks
- **Alert Management**: Cooldown periods and detection history
- **High Performance**: Optimized for real-time processing
- **Easy Configuration**: Simple setup and configuration

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd Weapon-Detection-YOLOv5-main

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

#### Webcam Detection
```bash
python run_surveillance.py --mode webcam
```

#### Web-based Dashboard
```bash
python run_surveillance.py --mode web-server
```
Then open http://localhost:5000 in your browser.

#### IP Camera Detection
```bash
python run_surveillance.py --mode ip-camera
```

### 3. Advanced Usage

```bash
# Custom confidence threshold
python run_surveillance.py --mode webcam --confidence 0.7

# Save processed video
python run_surveillance.py --mode webcam --save-video

# Run web server on custom port
python run_surveillance.py --mode web-server --port 8080

# Enable debug mode
python run_surveillance.py --mode web-server --debug
```

## 📁 Project Structure

```
Weapon-Detection-YOLOv5-main/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── yolov5s.pt                        # Pre-trained YOLOv5 model
├── weapon_detector.py                # Core detection system
├── surveillance_server.py            # Web-based dashboard server
├── ip_camera_detector.py             # IP camera support
├── notification_system.py            # Alert notification system
├── run_surveillance.py               # Main execution script
└── templates/
    └── dashboard.html                # Web dashboard interface
```

## 🔧 Configuration

### Notification System

Create a `notification_config.json` file to configure alerts:

```json
{
    "email": {
        "enabled": true,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your-email@gmail.com",
        "password": "your-app-password",
        "recipients": ["security@company.com"]
    },
    "sms": {
        "enabled": true,
        "twilio_account_sid": "your-account-sid",
        "twilio_auth_token": "your-auth-token",
        "twilio_phone_number": "+1234567890",
        "recipients": ["+1234567890"]
    },
    "webhook": {
        "enabled": true,
        "url": "https://your-webhook-url.com/alerts",
        "headers": {
            "Authorization": "Bearer your-token"
        }
    },
    "alert_cooldown": 300
}
```

### IP Camera Setup

For IP camera mode, update the camera configurations in `run_surveillance.py`:

```python
camera_configs = [
    {
        'id': 'cam1',
        'url': 'rtsp://username:password@192.168.1.100:554/stream',
        'name': 'Main Entrance'
    },
    {
        'id': 'cam2',
        'url': 'http://192.168.1.102:8080/video',
        'name': 'Reception Area'
    }
]
```

## 🎮 Web Dashboard

The web-based dashboard provides:

- **Live Video Feed**: Real-time surveillance with weapon detection overlays
- **Detection Statistics**: Count of total detections, knife detections, pistol detections
- **Alert History**: Recent weapon detection alerts with timestamps
- **Camera Controls**: Start/stop camera, clear history
- **Real-time Updates**: WebSocket-based live updates

Access the dashboard at: http://localhost:5000

## 📊 Detection Classes

The system detects two weapon classes:

1. **Knife** - Various types of knives and bladed weapons
2. **Pistol** - Handguns and pistols

## 🔍 Model Performance

Based on the training statistics:

| Class | Images | Labels | Precision | Recall | mAP@.5 | mAP@.5:.95 |
|-------|--------|--------|-----------|--------|--------|------------|
| All   | 697    | 799    | 0.92      | 0.839  | 0.91   | 0.618      |
| Knife | 697    | 320    | 0.917     | 0.884  | 0.936  | 0.589      |
| Pistol| 697    | 479    | 0.922     | 0.793  | 0.884  | 0.647      |

## 🛠️ API Endpoints

### Web Server API

- `GET /` - Main dashboard
- `GET /api/stats` - Get detection statistics
- `GET /api/history` - Get detection history
- `POST /api/start_camera` - Start camera processing
- `POST /api/stop_camera` - Stop camera processing
- `POST /api/clear_history` - Clear detection history

### WebSocket Events

- `video_frame` - Live video frame with detections
- `weapon_alert` - Weapon detection alert
- `connect` - Client connection
- `disconnect` - Client disconnection

## 🔒 Security Features

- **Alert Cooldown**: Prevents spam alerts for the same location
- **Detection History**: Maintains log of all detections
- **Image Capture**: Saves alert images for evidence
- **Real-time Monitoring**: Continuous surveillance with instant alerts
- **Multi-channel Notifications**: Email, SMS, and webhook alerts

## 📱 Mobile Support

The web dashboard is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- Security monitoring stations

## 🚨 Alert System

When a weapon is detected:

1. **Visual Alert**: Bounding box around detected weapon
2. **Console Log**: Detailed detection information
3. **Image Capture**: Alert image saved with timestamp
4. **Real-time Notification**: Instant alert to security staff
5. **Dashboard Update**: Live update on web interface

## 🔧 Troubleshooting

### Common Issues

1. **Camera not opening**: Check camera permissions and USB connection
2. **Model not loading**: Ensure `yolov5s.pt` is in the project directory
3. **Low detection accuracy**: Adjust confidence threshold with `--confidence` parameter
4. **IP camera connection**: Verify camera URL and credentials

### Performance Optimization

- Use GPU acceleration if available
- Adjust confidence threshold based on requirements
- Limit number of simultaneous camera streams
- Use appropriate video resolution

## 📈 Future Enhancements

- [ ] Support for more weapon types
- [ ] Face recognition integration
- [ ] Mobile app for security staff
- [ ] Cloud storage integration
- [ ] Advanced analytics dashboard
- [ ] Integration with existing security systems

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is for educational and security purposes. Please ensure compliance with local laws and regulations when using this system.

## ⚠️ Disclaimer

This system is designed for security and surveillance purposes. Users are responsible for ensuring compliance with applicable laws and regulations regarding surveillance and privacy in their jurisdiction.

---

**🛡️ Stay Safe - Real-time Weapon Detection for Enhanced Security**