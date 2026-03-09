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
  timeout: 120000,
});

const ImageDetection = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [confidence, setConfidence] = useState(0.5);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

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
      const formData = new FormData();
      formData.append('file', file);
      formData.append('confidence', confidence);

      const response = await api.post('/api/detect/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err) {
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
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              disabled={loading}
            />
          </div>
        )}

        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Detecting vehicles...</p>
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
            <div className="result-image">
              <img src={result.annotated_image} alt="Detected vehicles" />
            </div>

            <div className="result-stats">
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

              {result.detections.length > 0 && (
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
              )}

              <button
                className="btn-secondary"
                onClick={() => {
                  setResult(null);
                  fileInputRef.current?.click();
                }}
              >
                Detect Another Image
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageDetection;
