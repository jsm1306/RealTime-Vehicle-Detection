#!/usr/bin/env python3
"""Download YOLO model from GitHub if not present"""

import os
import sys
from pathlib import Path
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_model(url, destination):
    """Download file from URL with progress"""
    try:
        logger.info(f"Downloading model from {url}...")
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(destination, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        logger.info(f"Downloaded: {percent:.1f}%")
        
        logger.info(f"Model downloaded successfully to {destination}")
        return True
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        return False

def main():
    model_path = Path(__file__).parent / "best (1).pt"
    
    # If model already exists, skip download
    if model_path.exists():
        logger.info(f"Model already exists at {model_path}")
        return True
    
    logger.info(f"Model not found at {model_path}. Attempting to download...")
    
    # GitHub raw content URL
    github_url = "https://github.com/jsm1306/RealTime_VehicleDetection/raw/main/best%20(1).pt"
    
    # Try to download
    if download_model(github_url, str(model_path)):
        logger.info("✓ Model setup complete!")
        return True
    else:
        logger.error("✗ Failed to download model. Please upload it manually or check GitHub URL.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
