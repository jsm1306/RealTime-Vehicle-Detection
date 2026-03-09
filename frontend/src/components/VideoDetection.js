import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './Detection.css';

// Configure axios with proper base URL
const getAPIBaseURL = () => {
  // In production, use the window location's origin
  // In development with Docker, the backend is usually on the same host
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  // Default to current location origin
  return window.location.origin;
};

const api = axios.create({
  baseURL: getAPIBaseURL(),
  timeout: 600000, // 10 minutes for long-running operations
});

const VideoDetection = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [confidence, setConfidence] = useState(0.5);
  const [dragActive, setDragActive] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleDetection = async (file) => {
    if (!file) return;

    // Validate file type
    const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm'];
    if (!validTypes.includes(file.type)) {
      setError('Please upload a valid video file (MP4, AVI, MOV, MKV, WebM)');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('confidence', confidence);

      const response = await api.post('/api/detect/video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setProgress(Math.min(percentCompleted, 90)); // Cap at 90% during upload
          }
        },
      });

      setProgress(100);
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

  const downloadFile = (downloadUrl) => {
    // Ensure we have the full URL
    const fullUrl = downloadUrl.startsWith('http') 
      ? downloadUrl 
      : `${getAPIBaseURL()}${downloadUrl}`;
    
    // Use fetch to download the file
    fetch(fullUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.blob();
      })
      .then(blob => {
        // Create a temporary URL for the blob
        const url = window.URL.createObjectURL(blob);
        // Create a temporary anchor element to trigger download
        const link = document.createElement('a');
        link.href = url;
        link.download = result.output_video.split('/').pop() || 'detected_video.mp4';
        document.body.appendChild(link);
        link.click();
        // Clean up
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      })
      .catch(err => {
        setError(`Download error: ${err.message}`);
      });
  };

  return (
    <div className="detection-container">
      <div className="detection-card">
        <h2>Video Detection</h2>

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
            onClick={() => !loading && fileInputRef.current?.click()}
          >
            <div className="upload-content">
              <h3>Upload a Video</h3>
              <p>Drag and drop your video here, or click to browse</p>
              <p style={{ fontSize: '0.85rem', opacity: 0.7 }}>
                Supported formats: MP4, AVI, MOV, MKV, WebM
              </p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              disabled={loading}
            />
          </div>
        )}

        {loading && (
          <div className="loading-container">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
            <p>Processing video... {progress}%</p>
            <p style={{ fontSize: '0.85rem', opacity: 0.7 }}>This may take a few minutes</p>
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
            <div className="result-stats">
              <h3>Video Detection Results</h3>
              
              {/* Detection Statistics */}
              <div className="stats-section">
                <h4>Detection Statistics</h4>
                <div className="stats-grid">
                  <div className="stat-box">
                    <span className="stat-label">Total Detections</span>
                    <span className="stat-value">{result.statistics.total_detections}</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-label">Frames Processed</span>
                    <span className="stat-value">{result.statistics.processed_frames}</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-label">Avg per Frame</span>
                    <span className="stat-value">{result.statistics.avg_detections_per_frame}</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-label">Total Frames</span>
                    <span className="stat-value">{result.statistics.total_frames}</span>
                  </div>
                </div>
              </div>

              {/* Performance Metrics */}
              {result.performance_metrics && (
                <div className="stats-section">
                  <h4>Performance Metrics</h4>
                  <div className="stats-grid">
                    <div className="stat-box">
                      <span className="stat-label">Inference Speed</span>
                      <span className="stat-value">{result.performance_metrics.avg_inference_time_ms}ms</span>
                      <span className="stat-sublabel">per frame</span>
                    </div>
                    <div className="stat-box">
                      <span className="stat-label">Processing Speed</span>
                      <span className="stat-value">{result.performance_metrics.processing_fps}</span>
                      <span className="stat-sublabel">fps</span>
                    </div>
                    <div className="stat-box">
                      <span className="stat-label">Total Time</span>
                      <span className="stat-value">{result.performance_metrics.total_processing_time_seconds}s</span>
                      <span className="stat-sublabel">processing</span>
                    </div>
                    <div className="stat-box">
                      <span className="stat-label">Input Video FPS</span>
                      <span className="stat-value">{result.performance_metrics.input_video_fps}</span>
                      <span className="stat-sublabel">original</span>
                    </div>
                  </div>
                </div>
              )}

              <div className="action-buttons">
                <button
                  className="btn-primary"
                  onClick={() => downloadFile(result.output_video)}
                >
                  Download Processed Video
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => {
                    setResult(null);
                    fileInputRef.current?.click();
                  }}
                >
                  Detect Another Video
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoDetection;
