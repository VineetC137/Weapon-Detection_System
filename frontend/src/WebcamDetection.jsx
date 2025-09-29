import React, { useState, useRef, useEffect } from 'react';
import { Camera, CameraOff, AlertTriangle, Play, Square } from 'lucide-react';
import './WebcamDetection.css';

const WebcamDetection = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [detections, setDetections] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stream, setStream] = useState(null);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);

  // WebSocket connection for real-time detection
  useEffect(() => {
    // Connect to Flask-SocketIO server
    wsRef.current = new WebSocket('ws://localhost:5000/socket.io/?transport=websocket');
    
    wsRef.current.onopen = () => {
      console.log('Connected to detection server');
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'detection') {
        setDetections(data.detections);
        drawDetections(data.detections);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Failed to connect to detection server');
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const startWebcam = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Request camera access
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'environment'
        },
        audio: false
      });

      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }

      // Start detection by sending video frames to backend
      startDetection(mediaStream);
      setIsStreaming(true);
      
    } catch (err) {
      console.error('Error accessing webcam:', err);
      setError('Failed to access webcam. Please ensure camera permissions are granted.');
    } finally {
      setIsLoading(false);
    }
  };

  const stopWebcam = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.srcObject = null;
    }
    
    setIsStreaming(false);
    setDetections([]);
    
    // Clear canvas
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    }
  };

  const startDetection = async (mediaStream) => {
    try {
      // Create a canvas to capture frames
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = 640;
      canvas.height = 480;

      const sendFrame = () => {
        if (!isStreaming) return;

        // Draw current video frame to canvas
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        
        // Convert to base64
        const frameData = canvas.toDataURL('image/jpeg', 0.8);
        
        // Send frame to backend for detection
        fetch('http://localhost:5000/detect/video', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            frame: frameData,
            timestamp: Date.now()
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.detections) {
            setDetections(data.detections);
            drawDetections(data.detections);
          }
        })
        .catch(error => {
          console.error('Detection error:', error);
        });

        // Continue sending frames
        if (isStreaming) {
          setTimeout(sendFrame, 100); // Send frame every 100ms (10 FPS)
        }
      };

      sendFrame();
      
    } catch (err) {
      console.error('Error starting detection:', err);
      setError('Failed to start weapon detection');
    }
  };

  const drawDetections = (detections) => {
    if (!canvasRef.current || !videoRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Match canvas size to video
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;

    // Draw detections
    detections.forEach(detection => {
      const { bbox, class: className, confidence } = detection;
      const [x1, y1, x2, y2] = bbox;

      // Set color based on weapon type
      ctx.strokeStyle = className === 'pistol' ? '#ff0000' : '#ffff00';
      ctx.lineWidth = 3;
      ctx.fillStyle = className === 'pistol' ? 'rgba(255, 0, 0, 0.1)' : 'rgba(255, 255, 0, 0.1)';

      // Draw bounding box
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
      ctx.fillRect(x1, y1, x2 - x1, y2 - y1);

      // Draw label
      ctx.fillStyle = className === 'pistol' ? '#ff0000' : '#ffff00';
      ctx.font = '16px Arial';
      ctx.fillText(`${className} ${(confidence * 100).toFixed(1)}%`, x1, y1 - 5);
    });
  };

  const getWeaponIcon = (weaponType) => {
    return weaponType === 'pistol' ? '🔫' : '🔪';
  };

  return (
    <div className="webcam-detection">
      <div className="webcam-header">
        <h2>🎥 Live Webcam Weapon Detection</h2>
        <div className="webcam-controls">
          {!isStreaming ? (
            <button 
              onClick={startWebcam} 
              disabled={isLoading}
              className="btn btn-start"
            >
              <Play size={16} />
              {isLoading ? 'Starting...' : 'Start Detection'}
            </button>
          ) : (
            <button 
              onClick={stopWebcam} 
              className="btn btn-stop"
            >
              <Square size={16} />
              Stop Detection
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <AlertTriangle size={16} />
          {error}
        </div>
      )}

      <div className="webcam-container">
        <div className="video-wrapper">
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            className="webcam-video"
            style={{ display: isStreaming ? 'block' : 'none' }}
          />
          <canvas
            ref={canvasRef}
            className="detection-overlay"
            style={{ display: isStreaming ? 'block' : 'none' }}
          />
          
          {!isStreaming && (
            <div className="webcam-placeholder">
              <Camera size={64} />
              <p>Click "Start Detection" to begin webcam weapon detection</p>
            </div>
          )}
        </div>

        <div className="detection-panel">
          <h3>🎯 Live Detections</h3>
          
          {detections.length === 0 ? (
            <div className="no-detections">
              <CameraOff size={32} />
              <p>No weapons detected</p>
            </div>
          ) : (
            <div className="detection-list">
              {detections.map((detection, index) => (
                <div key={index} className={`detection-item ${detection.class}`}>
                  <div className="detection-icon">{getWeaponIcon(detection.class)}</div>
                  <div className="detection-info">
                    <div className="detection-class">
                      {detection.class.toUpperCase()}
                    </div>
                    <div className="detection-confidence">
                      Confidence: {(detection.confidence * 100).toFixed(1)}%
                    </div>
                    <div className="detection-time">
                      {new Date(detection.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="webcam-stats">
        <div className="stat-card">
          <div className="stat-value">{detections.length}</div>
          <div className="stat-label">Current Detections</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{isStreaming ? 'Active' : 'Inactive'}</div>
          <div className="stat-label">Stream Status</div>
        </div>
      </div>
    </div>
  );
};

export default WebcamDetection;