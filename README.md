# SmartBand AI

A real-time wrist-worn activity recognition system built on the **Arduino Nano 33 BLE Sense Rev2**. An Edge Impulse deep learning model runs directly on the microcontroller, classifying 8 physical activities from IMU sensor data and streaming predictions to a mobile app over Bluetooth LE.

**Live App:** https://munazzahfatima.github.io/SmartBand-ai/smartband_ai.html

---

## Project Overview

```
IMU Sensors (6-axis)
  ax, ay, az, gx, gy, gz
        │
        ▼
  Spectral Analysis
  (78 spectral features)
        │
        ▼
  Dense Neural Network
  128 → 64 → 32 → 8 classes
        │
        ▼
  BLE Notification
  "PRED:walking:0.921:waving:0.045"
        │
        ▼
  SmartBand AI App
  (Live display + history + alerts)
```

---

## ML Model — Edge Impulse

### Dataset

| Property | Value |
|---|---|
| Total recording time | 1h 55m 14s |
| Training samples | 645 |
| Test samples | 146 |
| Total samples | 791 |
| Number of classes | 8 |

**Samples per class:**

| Activity | Samples |
|---|---|
| drinking | 85 |
| excercise | 80 |
| fall | 79 |
| idle | 80 |
| tremor | 83 |
| walking | 85 |
| waving | 79 |
| writing | 74 |

---

### Impulse Design

**Input block — Time Series Data**
- Input axes: `ax, ay, az, gx, gy, gz` (6-axis IMU)
- Window size: 10,000 ms
- Window stride: 486.55 ms
- Sampling frequency: 16 Hz
- Zero-pad data: enabled

**Processing block — Spectral Analysis**
- Extracts frequency-domain features from all 6 axes
- Output: **78 spectral features**

**Learning block — Classification (Keras)**
- Input: 78 spectral features
- Output: 8 activity classes

---

### Neural Network Architecture

```
┌─────────────────────────────────┐
│     Input Layer  (78 features)  │
├─────────────────────────────────┤
│     Dense Layer  (128 neurons)  │  ReLU
├─────────────────────────────────┤
│     Dense Layer  (64 neurons)   │  ReLU
├─────────────────────────────────┤
│     Dense Layer  (32 neurons)   │  ReLU
├─────────────────────────────────┤
│     Output Layer (8 classes)    │  Softmax
└─────────────────────────────────┘
```

**Training settings:**
- Training cycles (epochs): 100
- Optimizer: Learned optimizer (Edge Impulse EON)
- Loss function: Categorical Cross-Entropy
- Training processor: CPU

---

### Training Results

| Metric | Value |
|---|---|
| **Accuracy** | **97.7%** |
| **Loss** | **0.07** |
| Weighted avg Precision | 0.98 |
| Weighted avg Recall | 0.98 |
| Weighted avg F1 Score | 0.98 |
| Area under ROC Curve | 1.00 |

**Confusion Matrix (Validation Set):**

| | DRINKING | EXCERCISE | FALL | IDLE | TREMOR | WALKING | WAVING | WRITING | F1 |
|---|---|---|---|---|---|---|---|---|---|
| **DRINKING** | **94.7%** | 0% | 0% | 5.3% | 0% | 0% | 0% | 0% | 0.95 |
| **EXCERCISE** | 5.6% | **94.4%** | 0% | 0% | 0% | 0% | 0% | 0% | 0.97 |
| **FALL** | 0% | 0% | **100%** | 0% | 0% | 0% | 0% | 0% | 1.00 |
| **IDLE** | 0% | 0% | 0% | **100%** | 0% | 0% | 0% | 0% | 0.97 |
| **TREMOR** | 0% | 0% | 0% | 0% | **91.7%** | 0% | 8.3% | 0% | 0.96 |
| **WALKING** | 0% | 0% | 0% | 0% | 0% | **100%** | 0% | 0% | 1.00 |
| **WAVING** | 0% | 0% | 0% | 0% | 0% | 0% | **100%** | 0% | 0.98 |
| **WRITING** | 0% | 0% | 0% | 0% | 0% | 0% | 0% | **100%** | 1.00 |

5 out of 8 classes achieved 100% accuracy. The model is particularly strong at detecting falls, walking, waving, idle, and writing.

---

### On-Device Performance (Arduino Nano 33 BLE Sense Rev2)

| Metric | Value |
|---|---|
| Inferencing time | **1 ms** |
| Peak RAM usage | **1.7 KB** |
| Flash usage | **35.0 KB** |
| Engine | EON™ Compiler |

The EON Compiler optimizes the model specifically for the nRF52840 microcontroller, achieving 1ms inference — fast enough for real-time continuous classification.

---

## App Features

- **Live BLE connection** — connects directly to the Arduino over Bluetooth LE
- **Real-time display** — animated activity ring, confidence bars, top 2 predictions
- **Fall detection alert** — full-screen alert with 10-second countdown, auto-calls 112
- **Activity history** — timestamped log stored locally on your device
- **Activity distribution chart** — visual breakdown of all recorded activities
- **Data export** — download history as CSV or JSON
- **Persistent storage** — data survives app close using localStorage
- **Auto-reconnect** — reconnects automatically if BLE signal drops
- **PWA** — installable on Android as a home screen app, works offline

---

## Activity Classes

| Activity | Emoji | Description |
|---|---|---|
| walking | 🚶 | Normal walking gait |
| writing | ✍️ | Hand writing motion |
| waving | 🌊 | Waving hand gesture |
| drinking | 🥤 | Raising hand to mouth |
| excercise | 🏃 | General exercise motion |
| idle | 😴 | No significant movement |
| tremor | 📳 | Involuntary shaking |
| fall | ⚠️ | Sudden fall event |

---

## Project Structure

```
SmartBand-ai/
├── smartband_ai.html                          ← Mobile web app
├── manifest.json                              ← PWA manifest
├── sw.js                                      ← Service worker (offline)
├── README.md                                  ← This file
├── model/
│   └── model_info.py                          ← ML model documentation (Python)
└── nano_ble33_sense_rev2_fusion/
    └── nano_ble33_sense_rev2_fusion.ino       ← Arduino sketch (C++)
```

---

## Hardware

- Arduino Nano 33 BLE Sense Rev2
- Onboard BMI270 accelerometer + gyroscope
- Onboard BMM150 magnetometer
- nRF52840 SoC (Cortex-M4F, 64 MHz, 1MB Flash, 256KB RAM)

---

## Arduino Libraries Required

Install via Arduino IDE → Tools → Manage Libraries:

| Library | Purpose |
|---|---|
| `ArduinoBLE` | Bluetooth LE communication |
| `Arduino_BMI270_BMM150` | IMU sensor driver |
| `Smart_Wristband_Activity_Recognition_inferencing` | Edge Impulse model (install as .zip) |

---

## BLE Protocol

| Parameter | Value |
|---|---|
| Device name | `SmartBand` |
| Service UUID | `180C` |
| Characteristic UUID | `2A56` |
| Mode | Notify |
| Data format | `PRED:<label1>:<val1>:<label2>:<val2>` |

Example message:
```
PRED:walking:0.921:waving:0.045
```

---

## Deployment

The app is deployed on GitHub Pages and accessible at:

```
https://munazzahfatima.github.io/SmartBand-ai/smartband_ai.html
```

Open in **Chrome on Android** → tap 3-dot menu → **Add to Home Screen** to install as a native-like app.

Web Bluetooth requires Chrome on Android or Chrome on desktop. Safari and Firefox are not supported.

---

## Browser Compatibility

| Browser | BLE Support |
|---|---|
| Chrome on Android | ✅ Full support |
| Chrome on Windows/Mac | ✅ Full support |
| Samsung Internet | ⚠️ Partial |
| Firefox | ❌ Not supported |
| Safari (iOS) | ❌ Not supported |

---

## Languages Used

| Language | Purpose |
|---|---|
| C++ (Arduino) | Firmware, IMU reading, ML inference, BLE transmission |
| Python | ML model documentation, dataset analysis |
| HTML / CSS / JavaScript | Mobile web app, BLE Web API, data storage |

---

## License

MIT License — free to use, modify, and distribute.
