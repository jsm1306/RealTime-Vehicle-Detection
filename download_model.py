#!/usr/bin/env python3
"""Download YOLO model from GitHub if not present"""

import os
import sys
from pathlib import Path
import urllib.request
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_model(url, destination, max_retries=3):
    """Download file from URL with retry logic"""
    for attempt in range(max_retries):
        try:
            logger.info(f"[Attempt {attempt + 1}/{max_retries}] Downloading model from {url}...")
            
            # Create parent directory if it doesn't exist
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            
            with urllib.request.urlopen(url, timeout=60) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                chunk_size = 1024 * 1024  # 1MB chunks for large files
                
                logger.info(f"File size: {total_size / (1024*1024):.2f} MB")
                
                with open(destination, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = (downloaded / total_size) * 100
                            logger.info(f"Progress: {percent:.1f}% ({downloaded / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB)")
            
            # Verify file was downloaded
            if Path(destination).exists():
                file_size = Path(destination).stat().st_size
                logger.info(f"✓ Model downloaded successfully! ({file_size / (1024*1024):.2f} MB)")
                return True
            else:
                logger.error("File was not saved properly")
                return False
                
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                logger.error(f"✗ Failed to download after {max_retries} attempts")
    
    return False

def main():
    model_path = Path(__file__).parent / "best (1).pt"
    
    # If model already exists, skip download
    if model_path.exists():
        file_size = model_path.stat().st_size
        logger.info(f"✓ Model already exists at {model_path} ({file_size / (1024*1024):.2f} MB)")
        return True
    
    logger.info(f"Model not found at {model_path}. Attempting to download...")
    
    # GitHub raw content URL
    github_url = "https://github.com/jsm1306/RealTime-Vehicle-Detection/raw/main/best%20(1).pt"
    
    # Try to download
    if download_model(github_url, str(model_path)):
        logger.info("✓ Model setup complete!")
        return True
    else:
        logger.error("✗ Failed to download model from GitHub.")
        logger.error(f"URL: {github_url}")
        logger.error("Steps to fix:")
        logger.error("1. Verify the model file exists on GitHub at the root of main branch")
        logger.error("2. Try downloading manually to test the URL")
        logger.error("3. Alternatively, upload the model file to cloud storage (e.g., AWS S3) and update the URL")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
