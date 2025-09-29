import { useState, useEffect } from 'react'
import WebcamDetection from './WebcamDetection'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('upload') // 'upload' or 'webcam'
  const [image, setImage] = useState(null)
  const [processedImage, setProcessedImage] = useState(null)
  const [detections, setDetections] = useState([])
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [alertTriggered, setAlertTriggered] = useState(false)

  // Fetch detection statistics
  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 5000) // Update stats every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setImage(e.target.result)
        setProcessedImage(null)
        setDetections([])
        setAlertTriggered(false)
      }
      reader.readAsDataURL(file)
    }
  }

  const detectWeapons = async () => {
    if (!image) return
    
    setLoading(true)
    try {
      const response = await fetch('http://localhost:5000/detect-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image }),
      })

      if (response.ok) {
        const data = await response.json()
        setProcessedImage(data.processed_image)
        setDetections(data.detections || [])
        setAlertTriggered(data.alert_triggered || false)
        fetchStats() // Update stats after detection
      } else {
        console.error('Detection failed')
      }
    } catch (error) {
      console.error('Error during detection:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🛡️ Weapon Detection System</h1>
        <p>AI-powered weapon detection using YOLOv5</p>
      </header>

      {/* Navigation Tabs */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          📤 Image Upload
        </button>
        <button 
          className={`tab-button ${activeTab === 'webcam' ? 'active' : ''}`}
          onClick={() => setActiveTab('webcam')}
        >
          📹 Live Webcam
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'upload' && (
        <div className="tab-content">
          <div className="container">
            <div className="upload-section">
              <h2>Upload Image for Detection</h2>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="file-input"
                id="image-upload"
              />
              <label htmlFor="image-upload" className="upload-button">
                Choose Image
              </label>
              
              {image && (
                <button 
                  onClick={detectWeapons} 
                  disabled={loading}
                  className="detect-button"
                >
                  {loading ? '🔍 Detecting...' : '🔍 Detect Weapons'}
                </button>
              )}
            </div>

            {alertTriggered && (
              <div className="alert-banner">
                ⚠️ WEAPON DETECTED! Alert has been triggered.
              </div>
            )}

            <div className="results-section">
              {image && (
                <div className="image-comparison">
                  <div className="image-container">
                    <h3>Original Image</h3>
                    <img src={image} alt="Original" className="result-image" />
                  </div>
                  
                  {processedImage && (
                    <div className="image-container">
                      <h3>Processed Image</h3>
                      <img src={processedImage} alt="Processed" className="result-image" />
                    </div>
                  )}
                </div>
              )}

              {detections.length > 0 && (
                <div className="detections-section">
                  <h3>🔍 Detections ({detections.length})</h3>
                  <div className="detections-grid">
                    {detections.map((detection, index) => (
                      <div key={index} className={`detection-card ${detection.class}`}>
                        <div className="detection-header">
                          <span className="detection-class">{detection.class.toUpperCase()}</span>
                          <span className="detection-confidence">
                            {Math.round(detection.confidence * 100)}%
                          </span>
                        </div>
                        <div className="detection-details">
                          <p>Position: ({detection.x}, {detection.y})</p>
                          <p>Size: {detection.width}×{detection.height}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {stats && (
              <div className="stats-section">
                <h3>📊 Detection Statistics</h3>
                <div className="stats-grid">
                  <div className="stat-card">
                    <h4>Total Detections</h4>
                    <p className="stat-value">{stats.total_detections || 0}</p>
                  </div>
                  <div className="stat-card">
                    <h4>🔪 Knives</h4>
                    <p className="stat-value">{stats.knife_detections || 0}</p>
                  </div>
                  <div className="stat-card">
                    <h4>🔫 Pistols</h4>
                    <p className="stat-value">{stats.pistol_detections || 0}</p>
                  </div>
                  <div className="stat-card">
                    <h4>📧 Alerts Sent</h4>
                    <p className="stat-value">{stats.alerts_sent || 0}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'webcam' && (
        <div className="tab-content">
          <WebcamDetection />
        </div>
      )}

      <footer className="app-footer">
        <p>Powered by YOLOv5 | Real-time Weapon Detection System</p>
      </footer>
    </div>
  )
}

export default App
