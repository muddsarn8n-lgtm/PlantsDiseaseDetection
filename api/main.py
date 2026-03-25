import os
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import httpx
from io import BytesIO
from PIL import Image
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TF_SERVING_URL = os.getenv("TF_SERVING_URL", "http://localhost:8501/v1/models/potato_disease_model:predict")

CLASS_NAMES = ["Potato___Early_blight", "Potato___Late_blight", "Potato___healthy"]


def read_image(data: bytes) -> np.ndarray:
    image = Image.open(BytesIO(data))
    image = image.convert("RGB")
    image = np.array(image)
    return image


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_data = await file.read()
    image = read_image(image_data)
    image_batch = np.expand_dims(image, axis=0).tolist()

    payload = {"instances": image_batch}

    async with httpx.AsyncClient() as client:
        response = await client.post(TF_SERVING_URL, json=payload)
        response.raise_for_status()

    predictions = response.json()["predictions"][0]
    predicted_class_idx = np.argmax(predictions)
    confidence = float(np.max(predictions))

    return {
        "class": CLASS_NAMES[predicted_class_idx],
        "confidence": round(confidence * 100, 2),
    }


@app.get("/treatment/{disease}")
async def get_treatment(disease: str):
    # TODO: Replace dummy responses with actual treatment information
    treatments = {
        "Potato___Early_blight": {
            "disease": "Early Blight",
            "treatment": "This is a dummy treatment for Early Blight. Actual treatment info coming soon.",
        },
        "Potato___Late_blight": {
            "disease": "Late Blight",
            "treatment": "This is a dummy treatment for Late Blight. Actual treatment info coming soon.",
        },
        "Potato___healthy": {
            "disease": "Healthy",
            "treatment": "Your potato plant is healthy! No treatment needed.",
        },
    }

    if disease in treatments:
        return treatments[disease]
    return {"disease": disease, "treatment": "No treatment information available."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
