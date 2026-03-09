# 🚗 Vehicle Detection System - Deployment Guide

A modern, professional AI dashboard for real-time vehicle detection using YOLOv8. Detect vehicles in images and videos with advanced analytics and a beautiful, production-ready UI.

## ✨ Features

- 📸 **Image Detection** - Upload images and get instant vehicle detection
- 🎥 **Video Detection** - Process videos with frame-by-frame detection
- 📊 **Real-time Analytics** - View detection statistics and metrics
- 🎨 **Modern Dashboard** - Professional UI with glassmorphism effects
- ⚡ **Fast Inference** - YOLOv8 powered detection engine
- 📈 **Detailed Reports** - Confidence scores, bounding boxes, detection history
- 📱 **Responsive Design** - Works perfectly on desktop, tablet, mobile

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   Frontend (React + Modern UI)      │
│   https://...-frontend.onrender.com │
└──────────────┬──────────────────────┘
               │
        ┌──────▼─────────┐
        │  API Requests  │
        └──────┬─────────┘
               │
┌──────────────▼──────────────────────┐
│  Backend (FastAPI + YOLOv8)         │
│  https://...-backend.onrender.com   │
│  /api/detect/image                  │
│  /api/detect/video                  │
└──────────────┬──────────────────────┘
               │
       ┌───────▼────────┐
       │ YOLOv8 Model   │
       │ (best.pt)      │
       └────────────────┘
```

---

## 📋 Prerequisites

- **Node.js** 16+ (for frontend)
- **Python** 3.10+ (for backend)
- **Git** (for deployment)
- **Render.com** account (for cloud hosting)
- **GitHub** account (to host code)

---

## 🚀 Local Development (Optional)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python -m uvicorn main:app --reload
```

Backend will be available at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: `http://localhost:3000`

---

## 📤 Deploy to Render (Production)

### Step 1: Prepare Repository

1. **Initialize Git** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit - Vehicle Detection System"
```

2. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Create `vehicle-detection` repository
   - Push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/vehicle-detection.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Render

#### Option A: Using Blueprint (Automatic - Recommended)

1. Go to https://render.com (sign up if needed)
2. Click **New** → **Blueprint**
3. Connect your GitHub account
4. Select your `vehicle-detection` repository
5. Click **Create from Blueprint**
6. Wait for both services to deploy (~10-15 minutes)

**That's it!** Both frontend and backend are now deployed.

#### Option B: Manual Deployment

**Backend Service:**

1. Go to https://render.com/dashboard
2. Click **New** → **Web Service**
3. Select your GitHub repository
4. Configure:
   ```
   Name:           vehicle-detection-backend
   Runtime:        Python 3.10
   Build Command:  pip install -r backend/requirements.txt
   Start Command:  python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   Plan:           Free
   ```
5. Click **Create Web Service**
6. Copy the URL (e.g., `https://vehicle-detection-backend.onrender.com`)

**Frontend Service:**

1. Click **New** → **Web Service**
2. Select your GitHub repository
3. Configure:
   ```
   Name:           vehicle-detection-frontend
   Runtime:        Node
   Build Command:  cd frontend && npm install && npm run build
   Start Command:  cd frontend && npx serve -s build -l $PORT
   Plan:           Free
   
   Environment Variables:
   REACT_APP_API_URL = https://vehicle-detection-backend.onrender.com
   NODE_ENV = production
   ```
4. Click **Create Web Service**

---

## 📦 Model File Handling

### Option 1: Include in Repository (Recommended for small models)

If your `best.pt` model is < 50MB:
- Keep it in `/backend/models/best.pt`
- It will deploy automatically with the backend
- **No extra steps needed** ✅

Check model size:
```bash
# PowerShell
(Get-Item "backend/models/best.pt").Length / 1MB

# macOS/Linux
ls -lh backend/models/best.pt | awk '{print $5}'
```

### Option 2: Download at Runtime (For large models)

If your model is > 100MB, download it when backend starts:

Create `backend/model_handler.py`:
```python
import os
import subprocess
from ultralytics import YOLO

MODEL_PATH = "models/best.pt"

def load_model():
    """Load or download model"""
    if not os.path.exists(MODEL_PATH):
        print("🔄 Downloading model...")
        os.makedirs("models", exist_ok=True)
        # Download from your source
        subprocess.run([
            "wget",
            "https://your-model-url/best.pt",
            "-O",
            MODEL_PATH
        ])
    
    return YOLO(MODEL_PATH)
```

Update `backend/main.py` startup:
```python
from model_handler import load_model

@app.on_event("startup")
async def startup():
    global model
    model = load_model()
    print("✅ Model loaded!")
```

---

## 🔗 Access Your Deployed App

Once deployed, you'll have three URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | `https://vehicle-detection-frontend.onrender.com` | Main application |
| **Backend API** | `https://vehicle-detection-backend.onrender.com` | API endpoint |
| **API Docs** | `https://vehicle-detection-backend.onrender.com/docs` | Interactive API testing |

---

## 🛠️ Project Structure

```
vehicle-detection/
├── frontend/                    # React frontend
│   ├── public/
│   │   └── index.html          # Includes Inter font
│   ├── src/
│   │   ├── App.js              # Main component
│   │   ├── App.css             # Modern styling (redesigned)
│   │   ├── index.js
│   │   └── components/
│   │       ├── ImageDetection.js
│   │       ├── VideoDetection.js
│   │       └── Detection.css    # Professional component styles
│   ├── package.json
│   └── .env.production         # Production env vars
│
├── backend/                     # FastAPI backend
│   ├── main.py                 # FastAPI app, endpoints
│   ├── requirements.txt        # Python dependencies
│   ├── models/
│   │   └── best.pt            # YOLOv8 model
│   └── outputs/               # Detection results
│
├── docker-compose.yml         # Local Docker setup
├── Dockerfile.frontend        # Frontend container
├── Dockerfile.backend         # Backend container
├── render.yaml               # Render deployment config
│
└── Documentation/
    ├── README.md             # Original readme
    ├── DESIGN_GUIDE.md       # Design specifications
    ├── DEPLOYMENT_GUIDE.md   # Full deployment guide
    ├── VERIFICATION_GUIDE.md # Testing checklist
    └── ... other docs
```

---

## 📝 Environment Variables

### Backend (`.env` - Don't commit)

```
# Optional: Add if you have specific configs
PYTHON_VERSION=3.10
```

### Frontend (`.env.production`)

```
REACT_APP_API_URL=https://vehicle-detection-backend.onrender.com
NODE_ENV=production
```

---

## 🧪 Testing

### Test API Endpoints

Once deployed, test the API:

```bash
# Get API docs
curl https://vehicle-detection-backend.onrender.com/docs

# Health check
curl https://vehicle-detection-backend.onrender.com/
```

Or visit the interactive API docs at:
`https://vehicle-detection-backend.onrender.com/docs`

### Test Frontend

Visit: `https://vehicle-detection-frontend.onrender.com`

- Upload a test image
- Check detection results
- Verify metric cards display
- Test confidence slider
- Inspect detection details table

---

## 🎨 UI Design

The frontend features a **modern, professional dashboard**:

- 🎨 **Color Scheme**: Dark slate (#0f172a) + refined amber (#facc15)
- ✨ **Effects**: Glassmorphism with soft shadows
- 📱 **Responsive**: Perfect on desktop, tablet, mobile
- ⚡ **Smooth**: Professional animations and transitions
- ♿ **Accessible**: WCAG AA compliant

See `DESIGN_GUIDE.md` for complete design specifications.

---

## 📊 API Endpoints

### Image Detection

```
POST /api/detect/image
Content-Type: multipart/form-data

Parameters:
- file: Image file (JPG, PNG, GIF, BMP, WebP)
- confidence: Detection confidence threshold (0.0-1.0)

Response:
{
  "annotated_image": "base64_encoded_image",
  "detections_count": 5,
  "image_shape": {
    "width": 1920,
    "height": 1080
  },
  "detections": [
    {
      "class_name": "car",
      "confidence": 0.95,
      "bbox": {
        "x1": 100,
        "y1": 200,
        "x2": 300,
        "y2": 400
      }
    }
  ],
  "performance_metrics": {
    "inference_time_ms": 145
  }
}
```

### Video Detection

```
POST /api/detect/video
Content-Type: multipart/form-data

Parameters:
- file: Video file (MP4, AVI, MOV, MKV, WebM)
- confidence: Detection confidence threshold (0.0-1.0)

Response:
{
  "output_video": "base64_encoded_video",
  "frame_count": 300,
  "total_detections": 1500,
  "average_inference_time_ms": 142,
  "detections_per_frame": {...}
}
```

---

## ⚙️ Configuration

### Render Free Tier

**Limitations:**
- Services spin down after 15 minutes of inactivity
- 0.5 GB RAM
- Limited build time
- Suitable for development/testing

**Upgrade to Starter ($7/month):**
- 24/7 availability
- 1 GB RAM
- Better performance
- Better for production

### Auto-Deploy

Render automatically redeploys when you:
1. Push to GitHub
2. Click "Manual Deploy" in Render dashboard

---

## 🐛 Troubleshooting

### Frontend can't connect to backend
**Problem:** API requests fail  
**Solution:**
1. Check `REACT_APP_API_URL` environment variable
2. Verify backend service is running in Render dashboard
3. Clear browser cache and reload

### Model not found on Render
**Problem:** Backend crashes on startup  
**Solution:**
1. If model > 50MB, implement download at startup
2. Or, push model file to GitHub
3. Check Render logs for detailed error

### Build fails on Render
**Problem:** Deployment unsuccessful  
**Solution:**
1. Check build logs in Render dashboard
2. Verify `requirements.txt` has all dependencies
3. Test locally first: `pip install -r backend/requirements.txt`

### Slow first request
**Problem:** 15+ second delay on first request  
**Solution:**
- Normal on free tier (service spin-up)
- Upgrade to Starter plan for instant responses

---

## 📚 Documentation

- **DESIGN_GUIDE.md** - Complete design system
- **DEPLOYMENT_GUIDE.md** - Full deployment instructions
- **VERIFICATION_GUIDE.md** - Testing checklist
- **BEFORE_AFTER.md** - Design transformation
- **MODERN_DESIGN_IMPLEMENTATION.md** - Implementation details

---

## 🚀 Next Steps

1. ✅ Design complete (modern dashboard)
2. ⏳ Push to GitHub
3. ⏳ Deploy to Render (use render.yaml)
4. ⏳ Test live application
5. ⏳ Share with users!

---

## 💡 Tips

- Always test locally before pushing to GitHub
- Keep `.env` in `.gitignore` - don't commit secrets
- Use Render logs to debug issues
- Start with free tier, upgrade if needed
- Monitor usage in Render dashboard

---

## 📄 License

This project is open source. Feel free to modify and deploy!

---

## 🎯 Summary

```bash
# 1. Push to GitHub (one-time)
git push -u origin main

# 2. Deploy on Render (one-time)
# Go to render.com → New → Blueprint → Select repo

# 3. Done! 🎉
# Frontend: https://vehicle-detection-frontend.onrender.com
# Backend:  https://vehicle-detection-backend.onrender.com
```

**Your Vehicle Detection System is now production-ready!** ✨

---

**Questions?** Check the detailed guides in the documentation folder or visit:
- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- YOLOv8 Docs: https://docs.ultralytics.com
