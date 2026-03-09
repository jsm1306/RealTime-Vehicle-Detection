from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from pathlib import Path
import uuid
import tempfile
import os
from ultralytics import YOLO
import logging
from typing import Optional
import base64
import io
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vehicle Detection API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model path
BACKEND_DIR = Path(__file__).parent.absolute()
MODEL_PATH = BACKEND_DIR.parent / "best (1).pt"
OUTPUT_DIR = BACKEND_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
logger.info(f"Output directory: {OUTPUT_DIR}")

# Load YOLO model
def load_model():
    """Load YOLO model with detailed logging"""
    try:
        if not MODEL_PATH.exists():
            logger.error(f"Model file not found at {MODEL_PATH}")
            logger.error(f"Expected path: {MODEL_PATH.absolute()}")
            return None
        
        logger.info(f"Loading model from {MODEL_PATH}")
        model = YOLO(MODEL_PATH)
        logger.info(f"✓ Model loaded successfully from {MODEL_PATH}")
        return model
    except Exception as e:
        logger.error(f"✗ Failed to load model: {e}", exc_info=True)
        return None

model = load_model()

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "Online",
        "message": "Vehicle Detection API is running",
        "endpoints": {
            "detect_image": "/api/detect/image",
            "detect_video": "/api/detect/video",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
async def health_check():
    """Check API and model health"""
    health_status = {
        "status": "healthy" if model else "error",
        "model_loaded": model is not None,
        "model_path": str(MODEL_PATH),
        "model_exists": MODEL_PATH.exists(),
        "api_running": True,
    }
    
    if not model:
        health_status["error"] = "Model failed to load. Check /api/health for details."
        health_status["model_path_expected"] = str(MODEL_PATH.absolute())
    
    return health_status


@app.post("/api/detect/image")
async def detect_image(
    file: UploadFile = File(...),
    confidence: float = 0.5
):
    """
    Detect vehicles in an image
    - **file**: Image file (JPG, PNG, etc.)
    - **confidence**: Detection confidence threshold (0-1)
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    if confidence < 0 or confidence > 1:
        raise HTTPException(status_code=400, detail="Confidence must be between 0 and 1")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )

    try:
        # Read image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Failed to decode image")

        # Run inference with timing
        inference_start = time.time()
        results = model.predict(source=image, conf=confidence, verbose=False)
        result = results[0]
        inference_time = time.time() - inference_start

        # Extract detection data
        detections = []
        for box in result.boxes:
            detections.append({
                "class": int(box.cls[0]),
                "class_name": model.names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "bbox": {
                    "x1": float(box.xyxy[0][0]),
                    "y1": float(box.xyxy[0][1]),
                    "x2": float(box.xyxy[0][2]),
                    "y2": float(box.xyxy[0][3])
                }
            })

        # Draw boxes on image
        annotated_image = result.plot()

        # Convert to base64 for response
        _, buffer = cv2.imencode('.jpg', annotated_image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        return JSONResponse({
            "status": "success",
            "detections_count": len(detections),
            "detections": detections,
            "annotated_image": f"data:image/jpeg;base64,{image_base64}",
            "image_shape": {
                "height": image.shape[0],
                "width": image.shape[1]
            },
            "performance_metrics": {
                "inference_time_ms": round(inference_time * 1000, 2)
            }
        })

    except Exception as e:
        logger.error(f"Error in image detection: {e}")
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")


@app.post("/api/detect/video")
async def detect_video(
    file: UploadFile = File(...),
    confidence: float = 0.5,
    max_frames: Optional[int] = None
):
    """
    Detect vehicles in a video
    - **file**: Video file (MP4, AVI, etc.)
    - **confidence**: Detection confidence threshold (0-1)
    - **max_frames**: Maximum frames to process (None = all frames)
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    if confidence < 0 or confidence > 1:
        raise HTTPException(status_code=400, detail="Confidence must be between 0 and 1")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )

    try:
        # Record total processing time
        processing_start = time.time()
        
        # Save uploaded video temporarily (cross-platform)
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_input_path = os.path.join(temp_dir, f"{uuid.uuid4()}{file_ext}")
        with open(temp_input_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # Process video
        output_filename = f"detected_{uuid.uuid4()}.mp4"
        output_path = OUTPUT_DIR / output_filename

        cap = cv2.VideoCapture(temp_input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        out = cv2.VideoWriter(
            str(output_path),
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (width, height)
        )

        frame_count = 0
        detection_stats = {"total_vehicles": 0, "frames_processed": 0}
        inference_times = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if max_frames and frame_count >= max_frames:
                break

            # Run inference with timing
            inference_start = time.time()
            results = model.predict(source=frame, conf=confidence, verbose=False)
            result = results[0]
            inference_time = time.time() - inference_start
            inference_times.append(inference_time)

            # Count detections
            detection_stats["total_vehicles"] += len(result.boxes)
            detection_stats["frames_processed"] += 1

            # Draw boxes
            annotated_frame = result.plot()
            out.write(annotated_frame)

            frame_count += 1

        cap.release()
        out.release()

        # Calculate timing statistics
        total_processing_time = time.time() - processing_start
        avg_inference_time = (sum(inference_times) / len(inference_times)) if inference_times else 0
        processing_fps = detection_stats["frames_processed"] / total_processing_time if total_processing_time > 0 else 0

        # Clean up temp file
        if os.path.exists(temp_input_path):
            try:
                os.remove(temp_input_path)
            except Exception as e:
                logger.warning(f"Failed to clean temp file: {e}")

        # Return download URL with performance metrics
        return JSONResponse({
            "status": "success",
            "output_video": f"/api/download/{output_filename}",
            "statistics": {
                "total_frames": total_frames,
                "processed_frames": detection_stats["frames_processed"],
                "total_detections": detection_stats["total_vehicles"],
                "avg_detections_per_frame": round(
                    detection_stats["total_vehicles"] / max(detection_stats["frames_processed"], 1), 2
                )
            },
            "performance_metrics": {
                "total_processing_time_seconds": round(total_processing_time, 2),
                "avg_inference_time_ms": round(avg_inference_time * 1000, 2),
                "processing_fps": round(processing_fps, 2),
                "input_video_fps": round(fps, 2)
            }
        })

    except Exception as e:
        logger.error(f"Error in video detection: {e}")
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download processed video"""
    file_path = OUTPUT_DIR / filename
    logger.info(f"Download requested: {filename} -> {file_path}")
    
    # Security: ensure file is within OUTPUT_DIR
    if not file_path.resolve().is_relative_to(OUTPUT_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
    
    logger.info(f"Serving file: {file_path}")
    return FileResponse(file_path, media_type="video/mp4", filename=filename)


@app.get("/api/models")
async def get_model_info():
    """Get information about the loaded model"""
    if model is None:
        return {"error": "Model not loaded"}
    return {
        "model_name": model.model_name,
        "classes": model.names,
        "num_classes": len(model.names),
        "model_type": "YOLOv8"
    }


if __name__ == "__main__":
    import uvicorn
    import os
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("BACKEND_PORT", "8000")))
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
