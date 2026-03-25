# Potato Disease Detection - Full Stack Solution

## Project Overview

End-to-end potato leaf disease classification system with 4 components:

1. **Training** (`load_dataset.ipynb`) — CNN model trained with TensorFlow/Keras
2. **API** (`api/`) — FastAPI backend that calls TF Serving for predictions → see [api/CLAUDE.md](api/CLAUDE.md)
3. **Frontend** (`frontend/`) — Web app for uploading images and viewing results → see [frontend/CLAUDE.md](frontend/CLAUDE.md)
4. **Mobile** (`mobile/`) — Flutter app (iOS + Android) for camera/gallery upload → see [mobile/CLAUDE.md](mobile/CLAUDE.md)

Classifies potato leaf images into 3 categories:

- `Potato___Early_blight`
- `Potato___Late_blight`
- `Potato___healthy`

## Architecture

```
User (Web/Mobile) → FastAPI (localhost:8000) → TF Serving (localhost:8501) → Saved Model
```

## Build Order

1. **Train the model** — run the notebook to train and export to `models/potato_disease_model/1/`
2. **Start TF Serving** — serve the exported model via Docker
3. **Start FastAPI** — `cd api && python main.py`
4. **Run Frontend** — `cd frontend && python -m http.server 3000`
5. **Run Mobile** — `cd mobile && flutter run`

## Dataset

- **Location**: `dataset/` directory with one subfolder per class containing `.JPG` images
- **Source**: PlantVillage dataset (potato subset)
- **Image format**: JPG, variable sizes, resized to 256x256 during loading

## How to Regenerate the Code from Scratch

### Prerequisites

1. Create a Python 3.13 virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install tensorflow numpy matplotlib
   ```

### Step-by-step instructions to build `load_dataset.ipynb`

Create a Jupyter notebook (`load_dataset.ipynb`) with the following steps. Each step should be its own cell with a markdown header above it.

#### 1. Setup and Imports
- Import: `tensorflow`, `keras`, `image_dataset_from_directory` (from `tensorflow.keras.preprocessing`), `numpy`, `matplotlib.pyplot`, `pathlib.Path`, `os`
- Print TF and Keras versions to verify installation

#### 2. Dataset Configuration
- Set constants:
  - `DATASET_PATH` = path to the `dataset/` folder (use absolute path)
  - `IMAGE_SIZE` = `(256, 256)`
  - `BATCH_SIZE` = `32`
  - `SEED` = `42`
- Verify the dataset path exists using `pathlib.Path`
- List and print all class directories found
- Count and print number of `.JPG` images per class

#### 3. Load Full Dataset
- Use `image_dataset_from_directory()` with:
  - `seed=SEED`
  - `image_size=IMAGE_SIZE`
  - `batch_size=BATCH_SIZE`
  - `shuffle=True` (shuffle the dataset)
  - Use default `label_mode` (integer labels)
- Print class names and total batch count

#### 4. Split Dataset - Train (80%) / Temp (20%)
- Calculate `train_size = int(0.8 * total_batches)`
- Use `.take(train_size)` for training set
- Use `.skip(train_size)` for the temp set (remaining 20%)

#### 5. Split Temp - Validation (10%) / Test (10%)
- Split the temp dataset 50/50 using `.take()` and `.skip()`
- Print batch counts and approximate image counts with percentages for all three splits

#### 6. Performance Optimization
- Define `SHUFFLE_BUFFER = 1000`
- Apply `.cache().shuffle(SHUFFLE_BUFFER).prefetch(tf.data.AUTOTUNE)` to all three datasets
- Order matters: cache first (avoid re-reading from disk), then shuffle (randomize batch order each epoch), then prefetch (overlap data loading with training)

#### 7. Build CNN Model
- Build a `keras.Sequential` model with preprocessing, augmentation, and conv layers baked in:
  1. **Preprocessing**: `Resizing(256, 256)` + `Rescaling(1./255)`
  2. **Augmentation** (only active during training): `RandomRotation(0.2)`, `RandomFlip("horizontal")`
  3. **Feature extraction**: 6x (`Conv2D` + `MaxPooling2D`) blocks — filters: 32 → 64 → 64 → 64 → 64 → 64, kernel `(3,3)`, `relu` activation
  4. **Classification head**: `Flatten()` → `Dense(64, relu)` → `Dense(3, softmax)`
- `INPUT_SHAPE = (BATCH_SIZE, 256, 256, 3)`
- Call `model.build(input_shape=INPUT_SHAPE)` then `model.summary()`

#### 8. Compile the Model
- Compile with:
  - `optimizer='adam'`
  - `loss=SparseCategoricalCrossentropy(from_logits=False)`
  - `metrics=['accuracy']`

#### 9. Train the Model
- Set `EPOCHS = 50`
- Call `model.fit(train_dataset, batch_size=BATCH_SIZE, epochs=EPOCHS, validation_data=val_dataset)`
- Save training history to `history` for later use

#### 10. Evaluate the Model
- Run `model.evaluate(test_dataset)`
- Print test loss and test accuracy percentage

#### 11. Predict on Sample Test Images
- Get a batch from test dataset
- Run `model.predict()` on first 3 images
- Display 1x3 grid with actual vs predicted labels, confidence %, green/red title color

#### 12. Save the Model
- `MODEL_VERSION = 1`
- Export as SavedModel for TF Serving: `model.export(f"models/potato_disease_model/{MODEL_VERSION}")`

## Key Design Decisions

- **Integer labels** (default `label_mode='int'`) — uses `SparseCategoricalCrossentropy` loss
- **Preprocessing inside the model** — `Resizing` + `Rescaling` + augmentation layers are part of the model, not the data pipeline. This means the saved model handles raw images directly at inference time.
- **Augmentation layers** are only active during `model.fit()` (training=True) — validation/test data passes through unaugmented
- **Shuffle enabled** (`shuffle=True`) in `image_dataset_from_directory` to randomize data order before splitting
- **Batch-level splitting** using `.take()` / `.skip()` on `tf.data.Dataset`
- **Cache -> Shuffle -> Prefetch** pipeline on all datasets for optimal I/O performance

## TF Serving Config

A config file at `models/models.config` defines the model for TF Serving:
- Model name: `potato_disease_model`
- Base path: `/models/potato_disease_model`
- Version policy: serve all versions (latest by default)

Start TF Serving via Docker:
```bash
docker run -p 8501:8501 \
  --mount type=bind,source=$(pwd)/models,target=/models \
  -t tensorflow/serving \
  --model_config_file=/models/models.config
```

## Component-Specific Instructions

Each component has its own CLAUDE.md with detailed regeneration instructions:

| Component | Location | CLAUDE.md |
|-----------|----------|-----------|
| Training notebook | `load_dataset.ipynb` | This file |
| FastAPI backend | `api/` | [api/CLAUDE.md](api/CLAUDE.md) |
| Web frontend | `frontend/` | [frontend/CLAUDE.md](frontend/CLAUDE.md) |
| Flutter mobile app | `mobile/` | [mobile/CLAUDE.md](mobile/CLAUDE.md) |
