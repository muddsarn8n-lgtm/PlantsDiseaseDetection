# Frontend - Potato Disease Detection

## Overview

Single-page web app that lets users upload a potato leaf image, sends it to the FastAPI backend for disease prediction via TF Serving, and displays the result with an option to view treatment information.

## Prerequisites

No build tools needed — it's a plain HTML/CSS/JS file. Just serve it with any HTTP server.

## How to Regenerate `index.html` from Scratch

Create a single file `index.html` with the following:

### 1. HTML Structure
- Container card centered on page with:
  - Title: "Potato Disease Detection"
  - Subtitle: "Upload a potato leaf image to detect disease"
  - Upload area (click or drag & drop) with hidden `<input type="file" accept="image/*">`
  - Image preview `<img>` (hidden by default)
  - "Predict Disease" button (disabled until image selected)
  - Result div containing:
    - Prediction label, class name, confidence percentage
    - "View Treatment" button (hidden until prediction succeeds)
    - Treatment result div (hidden until treatment is fetched)

### 2. CSS Styling
- System font stack, `#f0f2f5` background
- White card with `border-radius: 16px`, `box-shadow`, max-width `500px`
- Upload area: dashed `2px` border, turns solid green when image loaded
- Predict button: green (`#4CAF50`), full width, disabled state is grey
- Result card: green background (`#e8f5e9`) for success, red (`#ffebee`) for error
- Treatment button: blue (`#1976D2`)
- Spinner animation for loading state

### 3. JavaScript Logic

#### Configuration
- `BASE_URL` = `"http://localhost:8000"`
- `API_URL` = `${BASE_URL}/predict`

#### State
- `selectedFile` — the chosen image file
- `detectedDisease` — raw class name from API (e.g. `Potato___Early_blight`)

#### Upload Handling
- Click on upload area triggers file input
- Drag & drop support with `dragover`/`dragleave`/`drop` events
- `handleFile()`: reads file with `FileReader`, shows preview, enables predict button

#### Prediction
- On predict button click:
  - Create `FormData` with the file
  - `POST` to `/predict`
  - On success: store `detectedDisease`, display class name (with `Potato___` prefix stripped), confidence, show treatment button
  - On error: show error message

#### Treatment
- On "View Treatment" button click:
  - `GET` to `/treatment/{detectedDisease}`
  - On success: display treatment text, hide the button
  - On error: show failure message

## Running

```bash
cd frontend
python -m http.server 3000
```

Open `http://localhost:3000` in your browser.

**Important**: Do NOT open `index.html` as a `file:///` URL — CORS will block API requests. Must be served via HTTP.

## Key Design Decisions

- **No framework / no build step** — single HTML file with inline CSS and JS for simplicity
- **Drag & drop + click** — two ways to upload for convenience
- **Treatment button only appears after successful prediction** — clean progressive disclosure
- **Display name strips `Potato___` prefix** — cleaner UX
