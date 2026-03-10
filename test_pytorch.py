#!/usr/bin/env python3
"""
Test PyTorch model inference in isolated process
Run as: python test_pytorch.py
"""

import numpy as np
import cv2
from pathlib import Path
import time
import logging
from ultralytics import YOLO
import psutil
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_memory_usage():
    """Get current process memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def test_pytorch_model():
    """Test original PyTorch model"""
    logger.info("\n" + "="*60)
    logger.info("Testing PyTorch Model")
    logger.info("="*60)
    
    model_path = Path(__file__).parent / "best (1).pt"
    
    if not model_path.exists():
        logger.error(f"Model not found: {model_path}")
        return None
    
    # Create dummy image
    dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
    dummy_image[100:300, 100:300] = 255  # Add some content
    
    try:
        mem_start = get_memory_usage()
        logger.info(f"Starting memory: {mem_start:.2f} MB")
        
        # Load model
        load_start = time.time()
        model = YOLO(model_path)
        load_time = time.time() - load_start
        logger.info(f"✓ Model loaded in {load_time:.2f}s")
        
        mem_after_load = get_memory_usage()
        logger.info(f"Memory after load: {mem_after_load:.2f} MB (+{mem_after_load - mem_start:.2f} MB)")
        
        # Warm-up inference (ignored)
        logger.info("Warming up...")
        _ = model(dummy_image, verbose=False)
        
        # Actual inference test (5 runs)
        logger.info("Running 5 inference tests...")
        inference_times = []
        for i in range(5):
            inf_start = time.time()
            results = model(dummy_image, verbose=False)
            inf_time = time.time() - inf_start
            inference_times.append(inf_time)
            logger.info(f"  Inference {i+1}: {inf_time*1000:.2f}ms")
        
        avg_time = np.mean(inference_times)
        mem_final = get_memory_usage()
        
        logger.info(f"\n📊 PyTorch Results:")
        logger.info(f"  Avg inference time: {avg_time*1000:.2f}ms")
        logger.info(f"  Final memory: {mem_final:.2f} MB")
        logger.info(f"  Peak memory usage: {mem_after_load:.2f} MB")
        
        return {
            'type': 'pytorch',
            'load_time': load_time,
            'avg_inference_time': avg_time,
            'memory_mb': mem_final,
            'peak_memory_mb': mem_after_load
        }
    except Exception as e:
        logger.error(f"PyTorch test failed: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    result = test_pytorch_model()
    if result:
        logger.info("\n✅ PyTorch test completed successfully")
    else:
        logger.error("\n❌ PyTorch test failed")
