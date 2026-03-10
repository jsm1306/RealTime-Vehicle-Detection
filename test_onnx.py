#!/usr/bin/env python3
"""
Test ONNX model inference in isolated process
Run as: python test_onnx.py
"""

import numpy as np
import cv2
from pathlib import Path
import time
import logging
import psutil
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_memory_usage():
    """Get current process memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def test_onnx_model():
    """Test ONNX model"""
    logger.info("\n" + "="*60)
    logger.info("Testing ONNX Model")
    logger.info("="*60)
    
    onnx_path = Path(__file__).parent / "best (1).onnx"
    
    if not onnx_path.exists():
        logger.error(f"ONNX model not found: {onnx_path}")
        logger.info("Run 'python convert_to_onnx.py' first to create the ONNX model")
        return None
    
    try:
        import onnxruntime as ort
    except ImportError:
        logger.error("onnxruntime not installed. Install with: pip install onnxruntime")
        return None
    
    # Create dummy image
    dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
    dummy_image[100:300, 100:300] = 255
    
    try:
        mem_start = get_memory_usage()
        logger.info(f"Starting memory: {mem_start:.2f} MB")
        
        # Create session
        load_start = time.time()
        session = ort.InferenceSession(str(onnx_path))
        load_time = time.time() - load_start
        logger.info(f"✓ ONNX session created in {load_time:.2f}s")
        
        mem_after_load = get_memory_usage()
        logger.info(f"Memory after load: {mem_after_load:.2f} MB (+{mem_after_load - mem_start:.2f} MB)")
        
        # Get input name
        input_name = session.get_inputs()[0].name
        input_shape = session.get_inputs()[0].shape
        logger.info(f"Input: {input_name} {input_shape}")
        
        # Prepare input (normalize to 0-1)
        test_input = np.expand_dims(dummy_image, 0).astype(np.float32) / 255.0
        test_input = np.transpose(test_input, (0, 3, 1, 2))  # BHWC -> BCHW
        
        # Warm-up
        logger.info("Warming up...")
        _ = session.run(None, {input_name: test_input})
        
        # Actual inference test (5 runs)
        logger.info("Running 5 inference tests...")
        inference_times = []
        for i in range(5):
            inf_start = time.time()
            outputs = session.run(None, {input_name: test_input})
            inf_time = time.time() - inf_start
            inference_times.append(inf_time)
            logger.info(f"  Inference {i+1}: {inf_time*1000:.2f}ms")
        
        avg_time = np.mean(inference_times)
        mem_final = get_memory_usage()
        
        logger.info(f"\n📊 ONNX Results:")
        logger.info(f"  Avg inference time: {avg_time*1000:.2f}ms")
        logger.info(f"  Final memory: {mem_final:.2f} MB")
        logger.info(f"  Peak memory usage: {mem_after_load:.2f} MB")
        
        return {
            'type': 'onnx',
            'load_time': load_time,
            'avg_inference_time': avg_time,
            'memory_mb': mem_final,
            'peak_memory_mb': mem_after_load
        }
    except Exception as e:
        logger.error(f"ONNX test failed: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    result = test_onnx_model()
    if result:
        logger.info("\n✅ ONNX test completed successfully")
    else:
        logger.error("\n❌ ONNX test failed")
