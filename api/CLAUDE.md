# API - Potato Disease Detection

## Overview

FastAPI backend that acts as a bridge between clients (web frontend / mobile app) and TensorFlow Serving. It receives potato leaf images, forwards them to TF Serving for prediction, and returns the disease classification result.

## Prerequisites

```bash
pip install fastapi uvicorn pillow httpx numpy
```

## How to Regenerate `main.py` from Scratch

Create a single file `main.py` with the following:

### 1. Imports and App Setup
- Import: `FastAPI`, `File`, `UploadFile` from fastapi; `CORSMiddleware` from fastapi.middleware.cors; `numpy`, `httpx`, `BytesIO` from io, `Image` from PIL, `uvicorn`
- Create `FastAPI()` app instance
- Add CORS middleware with `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`

### 2. Configuration
- `TF_SERVING_URL` = `"http://localhost:8501/v1/models/potato_disease_model:predict"`
- `CLASS_NAMES` = `["Potato___Early_blight", "Potato___Late_blight", "Potato___healthy"]`

### 3. Helper Function
- `read_image(data: bytes) -> np.ndarray`: opens image bytes with PIL, converts to RGB, returns as numpy array

### 4. Endpoints

#### `GET /ping`
- Returns `{"status": "ok"}` — health check

#### `POST /predict`
- Accepts `file: UploadFile`
- Reads image bytes, converts to numpy array using `read_image()`
- Expands dims to create batch: `np.expand_dims(image, axis=0).tolist()`
- Sends `{"instances": image_batch}` to TF Serving via `httpx.AsyncClient`
- Parses response, gets `predictions[0]`
- Returns `{"class": CLASS_NAMES[idx], "confidence": percentage}`

#### `GET /treatment/{disease}`
- Accepts disease class name as path parameter (e.g. `Potato___Early_blight`)
- Returns dummy treatment info from a hardcoded dictionary
- TODO: Replace with actual treatment data in the future
- Returns `{"disease": display_name, "treatment": treatment_text}`

### 5. Entry Point
- `uvicorn.run(app, host="0.0.0.0", port=8000)`

## Running

### 1. Start TF Serving (via Docker)
```bash
docker run -p 8501:8501 \
  --mount type=bind,source=$(pwd)/../models,target=/models \
  -t tensorflow/serving \
  --model_config_file=/models/models.config
```

### 2. Start FastAPI
```bash
cd api
python main.py
```

API will be available at `http://localhost:8000`.

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ping` | Health check |
| POST | `/predict` | Upload image, get disease prediction |
| GET | `/treatment/{disease}` | Get treatment info for a disease |

## Key Design Decisions

- **CORS fully open** (`allow_origins=["*"]`) — required for web frontend and mobile app to make requests
- **httpx async client** — non-blocking calls to TF Serving
- **Host `0.0.0.0`** — allows connections from other devices on the network (needed for mobile testing)
- **Treatment endpoint is dummy** — returns placeholder text, to be replaced with real data
