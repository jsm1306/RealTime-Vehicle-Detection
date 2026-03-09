import React, { useState } from 'react';
import './App.css';
import ImageDetection from './components/ImageDetection';
import VideoDetection from './components/VideoDetection';

function App() {
  const [activeTab, setActiveTab] = useState('image');

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>Vehicle Detection</h1>
          <p>Real-time vehicle detection using YOLOv8</p>
        </div>
      </header>

      <div className="container">
        <nav className="nav-tabs">
          <button
            className={`tab-button ${activeTab === 'image' ? 'active' : ''}`}
            onClick={() => setActiveTab('image')}
          >
            Image Detection
          </button>
          <button
            className={`tab-button ${activeTab === 'video' ? 'active' : ''}`}
            onClick={() => setActiveTab('video')}
          >
            Video Detection
          </button>
        </nav>

        <div className="tab-content">
          {activeTab === 'image' && <ImageDetection />}
          {activeTab === 'video' && <VideoDetection />}
        </div>
      </div>

      <footer className="app-footer">
        <p>Powered by YOLOv8 | FastAPI Backend</p>
      </footer>
    </div>
  );
}

export default App;
