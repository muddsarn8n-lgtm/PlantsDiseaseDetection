# Mobile App - Potato Disease Detection

## Overview

Flutter app targeting iOS and Android that lets users take a photo or select an image from their gallery, sends it to the FastAPI backend for disease prediction via TF Serving, and displays the result with an option to view treatment information.

## Prerequisites

- Flutter SDK installed (tested with Flutter 3.41.5)
- Xcode (for iOS) and/or Android Studio (for Android)
- iOS Simulator or Android Emulator

## How to Regenerate from Scratch

### 1. Create Flutter Project

```bash
flutter create --org com.diseasedetection mobile
cd mobile
```

### 2. Add Dependencies to `pubspec.yaml`

Add under `dependencies`:
```yaml
image_picker: ^1.1.2
http: ^1.3.0
```

Run `flutter pub get`.

### 3. iOS Permissions

Add to `ios/Runner/Info.plist` (inside the `<dict>` block):
```xml
<key>NSCameraUsageDescription</key>
<string>This app needs camera access to take photos of potato leaves for disease detection.</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>This app needs photo library access to select images of potato leaves for disease detection.</string>
```

### 4. Build `lib/main.dart`

Replace the generated `main.dart` with:

#### App Setup
- `MaterialApp` with green color scheme, Material 3, no debug banner
- Single `HomePage` stateful widget

#### State Variables
- `_image` (File?) — selected image
- `_isLoading` (bool) — predict loading state
- `_predictedClass` (String?) — display name (e.g. "Early blight")
- `_rawClass` (String?) — raw API class name (e.g. "Potato___Early_blight")
- `_confidence` (double?) — prediction confidence
- `_error` (String?) — error message
- `_isLoadingTreatment` (bool) — treatment loading state
- `_treatment` (String?) — treatment text

#### Base URL
- Platform-aware getter: `http://10.0.2.2:8000` for Android emulator, `http://localhost:8000` for iOS simulator
- For physical devices, use the machine's local IP address

#### Image Picker
- `_showPickerOptions()`: shows bottom sheet with "Take Photo" (camera) and "Choose from Gallery" options
- `_pickImage(ImageSource)`: uses `image_picker` to get image, resets all state

#### Prediction
- `_predict()`: creates `MultipartRequest` to `$baseUrl/predict`, sends image file
- On 200: parses `class` and `confidence` from JSON response
- Stores raw class name for treatment endpoint

#### Treatment
- `_fetchTreatment()`: `GET` to `$baseUrl/treatment/$_rawClass`
- Parses and displays treatment text

#### UI Layout
- `Scaffold` with `AppBar` titled "Potato Disease Detection"
- `SingleChildScrollView` with padding
- **Image area**: `GestureDetector` → `Container` (300px height, rounded corners, dashed border). Shows placeholder icon or selected image
- **Predict button**: `FilledButton.icon` with spinner during loading, disabled until image selected
- **Result card**: green background with prediction class, confidence, "View Treatment" `OutlinedButton`
- **Treatment section**: appears inside result card after fetch, below a `Divider`
- **Error card**: red background with error message

## Running

```bash
# Start iOS Simulator
open -a Simulator

# Run the app
cd mobile
flutter run
```

## Key Design Decisions

- **Platform-aware API URL** — `10.0.2.2` for Android emulator (maps to host localhost), `localhost` for iOS simulator
- **image_picker** package — handles both camera and gallery with proper platform permissions
- **http** package — lightweight HTTP client for multipart upload and GET requests
- **Progressive UI** — treatment button only shows after successful prediction, treatment text replaces the button after fetch
- **Material 3** with green theme — matches the agricultural/plant context
