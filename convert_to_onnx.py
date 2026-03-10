#!/usr/bin/env python3
"""
Convert YOLOv8 model to ONNX format
ONNX models use significantly less memory (~50-60% reduction) and are faster on CPU
"""

from pathlib import Path
from ultralytics import YOLO
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_to_onnx():
    """Convert YOLOv8 model to ONNX format"""
    
    model_path = Path(__file__).parent / "best (1).pt"
    onnx_path = Path(__file__).parent / "best.onnx"
    
    if not model_path.exists():
        logger.error(f"❌ Model file not found: {model_path}")
        return False
    
    try:
        logger.info(f"Loading YOLOv8 model from {model_path}...")
        model = YOLO(model_path)
        logger.info("✓ Model loaded successfully")
        
        logger.info(f"Converting to ONNX format...")
        logger.info("This may take 2-5 minutes depending on model size...")
        
        # Export to ONNX
        # opset_version=12 for better compatibility
        # simplify=True reduces model size
        export_path = model.export(
            format='onnx',
            imgsz=640,
            half=False,  # Use float32 for CPU inference
            optimize=True,
            dynamic=False,
            simplify=True,
            opset=12
        )
        
        logger.info(f"✓ Model converted successfully!")
        logger.info(f"ONNX model saved to: {export_path}")
        
        # Check file sizes
        original_size_mb = model_path.stat().st_size / (1024 * 1024)
        onnx_size_mb = Path(export_path).stat().st_size / (1024 * 1024)
        reduction = ((original_size_mb - onnx_size_mb) / original_size_mb) * 100
        
        logger.info(f"\n📊 Model Comparison:")
        logger.info(f"  Original PT:  {original_size_mb:.2f} MB")
        logger.info(f"  ONNX:        {onnx_size_mb:.2f} MB")
        logger.info(f"  Reduction:   {reduction:.1f}%")
        
        logger.info(f"\n✅ Conversion complete! Ready for deployment.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = convert_to_onnx()
    exit(0 if success else 1)
