import React, { useState, useRef } from 'react';
import axios from 'axios';
import './Detection.css';

// Configure axios with proper base URL
const getAPIBaseURL = () => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  return window.location.origin;
};

const api = axios.create({
  baseURL: getAPIBaseURL(),
  timeout: 300000, // 5 minutes to handle cold starts on free tier
});

const ImageDetection = () => {
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [confidence, setConfidence] = useState(0.5);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const wakeUpBackend = async () => {
    try {
      setStatusMsg('Waking up server (free tier may take ~60s)...');
      await axios.get(`${getAPIBaseURL()}/api/health`, { timeout: 120000 });
    } catch (e) {
      // ignore errors, still try the main request
    }
  };

  const handleDetection = async (file) => {
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Please upload a valid image file (JPG, PNG, GIF, BMP, WebP)');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Wake up backend first (handles cold start on Render free tier)
      await wakeUpBackend();

      setStatusMsg('Running detection...');
      const formData = new FormData();
      formData.append('file', file);
      formData.append('confidence', confidence);

      const response = await api.post('/api/detect/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setStatusMsg('');
      setResult(response.data);
    } catch (err) {
      setStatusMsg('');
      setError(err.response?.data?.detail || err.message || 'An error occurred during detection');
    } finally {
      setLoading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleDetection(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files && files[0]) {
      handleDetection(files[0]);
    }
  };

  const downloadSampleImage = async () => {
    try {
      const apiUrl = `${getAPIBaseURL()}/api/sample-image`;
      const response = await fetch(apiUrl);
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}. Make sure backend is running on port 8000 for local development.`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'sample_vehicle.jpg';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(`Download failed: ${err.message}`);
    }
  };

  return (
    <div className="detection-container">
      <div className="detection-card">
        <h2>Image Detection</h2>

        <div className="control-panel">
          <label>
            Confidence Threshold: <strong>{(confidence * 100).toFixed(0)}%</strong>
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={confidence}
            onChange={(e) => setConfidence(parseFloat(e.target.value))}
            className="slider"
            disabled={loading}
          />
        </div>

        <div className="disclaimer">
          <p><strong>⚠️ Note:</strong> Running on Render's free-tier CPU. First request may take up to 1-2 minutes to wake server.</p>
        </div>

        <button 
          onClick={(e) => {
            e.stopPropagation();
            downloadSampleImage();
          }} 
          className="btn-download-sample"
          disabled={loading}
        >
          📥 Download Sample Image
        </button>
          <button
                className="btn-secondary"
                onClick={() => {
                  setResult(null);
                  fileInputRef.current?.click();
                }}
              >
                Detect Another Image
              </button>
        {!result && (
          <div
            className={`upload-area ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            
            <div className="upload-content">
              <h3>Upload an Image</h3>
              <p>Drag and drop your image here, or click to browse</p>
              <p style={{ fontSize: '0.85rem', opacity: 0.7 }}>
                Supported formats: JPG, PNG, GIF, BMP, WebP
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
                disabled={loading}
              />
            </div>
          </div>
        )}

        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>{statusMsg || 'Detecting vehicles...'}</p>
            {statusMsg && statusMsg.includes('Waking') && (
              <p style={{ fontSize: '0.8rem', opacity: 0.7 }}>
                The free-tier server sleeps when idle. This only happens once.
              </p>
            )}
          </div>
        )}

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
            <button onClick={() => setError(null)} className="close-btn">×</button>
          </div>
        )}

        {result && (
          <div className="result-container">
            {/* LEFT SIDE: Detection Image */}
            <div className="result-image">
              <img src={result.annotated_image} alt="Detected vehicles" />
            </div>

            {/* RIGHT SIDE: Detection Table */}
            {result.detections.length > 0 && (
              <div className="result-table-section">
                <div className="detections-list">
                  <h4>Detection Details:</h4>
                  <table>
                    <thead>
                      <tr>
                        <th>Class</th>
                        <th>Confidence</th>
                        <th>Position</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.detections.map((det, idx) => (
                        <tr key={idx}>
                          <td>{det.class_name}</td>
                          <td>{(det.confidence * 100).toFixed(1)}%</td>
                          <td>
                            ({Math.round(det.bbox.x1)}, {Math.round(det.bbox.y1)})
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* BOTTOM: Metrics and Stats */}
            <div className="result-stats-bottom">
              <h3>Detection Results</h3>
              
              <div className="stats-section">
                <h4>Detection Statistics</h4>
                <div className="stats-grid">
                  <div className="stat-box">
                    <span className="stat-label">Vehicles Detected</span>
                    <span className="stat-value">{result.detections_count}</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-label">Image Size</span>
                    <span className="stat-value">
                      {result.image_shape.width} × {result.image_shape.height}
                    </span>
                  </div>
                </div>
              </div>

              {result.performance_metrics && (
                <div className="stats-section">
                  <h4>Performance Metrics</h4>
                  <div className="stats-grid">
                    <div className="stat-box">
                      <span className="stat-label">Inference Speed</span>
                      <span className="stat-value">{result.performance_metrics.inference_time_ms}ms</span>
                    </div>
                  </div>
                </div>
              )}

              
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageDetection;
