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

CLASS_NAMES = [
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]


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
    treatments = {
        "Potato___Early_blight": {
            "disease": "Potato Early Blight",
            "treatment": "Apply fungicides containing chlorothalonil or mancozeb. Remove infected leaves. Ensure proper spacing for air circulation. Practice crop rotation.",
        },
        "Potato___Late_blight": {
            "disease": "Potato Late Blight",
            "treatment": "Apply fungicides containing metalaxyl or copper-based products. Remove and destroy infected plants immediately. Avoid overhead irrigation. Use resistant varieties.",
        },
        "Potato___healthy": {
            "disease": "Healthy Potato",
            "treatment": "Your potato plant is healthy! Continue regular watering and fertilization.",
        },
        "Tomato___Bacterial_spot": {
            "disease": "Tomato Bacterial Spot",
            "treatment": "Apply copper-based bactericides. Remove infected plant debris. Use disease-free seeds and transplants. Avoid overhead watering.",
        },
        "Tomato___Early_blight": {
            "disease": "Tomato Early Blight",
            "treatment": "Apply fungicides containing chlorothalonil or copper. Remove lower infected leaves. Mulch around plants to prevent soil splash. Practice crop rotation.",
        },
        "Tomato___Late_blight": {
            "disease": "Tomato Late Blight",
            "treatment": "Apply fungicides containing metalaxyl or chlorothalonil. Remove and destroy infected plants. Improve air circulation. Avoid wetting foliage.",
        },
        "Tomato___Leaf_Mold": {
            "disease": "Tomato Leaf Mold",
            "treatment": "Improve air circulation and reduce humidity. Apply fungicides containing chlorothalonil. Remove infected leaves. Avoid overhead watering.",
        },
        "Tomato___Septoria_leaf_spot": {
            "disease": "Tomato Septoria Leaf Spot",
            "treatment": "Apply fungicides containing chlorothalonil or copper. Remove infected lower leaves. Mulch to prevent soil splash. Practice crop rotation.",
        },
        "Tomato___Spider_mites Two-spotted_spider_mite": {
            "disease": "Tomato Spider Mites",
            "treatment": "Spray with insecticidal soap or neem oil. Increase humidity around plants. Introduce predatory mites. Remove heavily infested leaves.",
        },
        "Tomato___Target_Spot": {
            "disease": "Tomato Target Spot",
            "treatment": "Apply fungicides containing chlorothalonil or mancozeb. Remove infected plant debris. Ensure proper spacing for air circulation. Practice crop rotation.",
        },
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
            "disease": "Tomato Yellow Leaf Curl Virus",
            "treatment": "Control whitefly vectors with insecticides or reflective mulch. Remove and destroy infected plants. Use resistant varieties. Install insect-proof netting.",
        },
        "Tomato___Tomato_mosaic_virus": {
            "disease": "Tomato Mosaic Virus",
            "treatment": "Remove and destroy infected plants. Disinfect tools with bleach solution. Wash hands before handling plants. Use resistant varieties. Avoid tobacco products near plants.",
        },
        "Tomato___healthy": {
            "disease": "Healthy Tomato",
            "treatment": "Your tomato plant is healthy! Continue regular watering and fertilization.",
        },
    }

    if disease in treatments:
        return treatments[disease]
    return {"disease": disease, "treatment": "No treatment information available."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
