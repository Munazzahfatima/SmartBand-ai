# SmartBand AI

A real-time activity recognition app for the **Arduino Nano 33 BLE Sense Rev2**. The Arduino runs an Edge Impulse ML model that classifies 8 physical activities using the onboard IMU, then streams predictions to your phone over Bluetooth LE. The app displays live results, logs history, and alerts on fall detection.

---

## Demo

| Home Screen | History | Settings |
|---|---|---|
| Live activity + confidence % | Activity log + chart | BLE config + export |

---

## Features

- **Live BLE connection** — connects directly to the Arduino over Bluetooth LE
- **8 activity classes** — Walking, Writing, Waving, Drinking, Exercise, Idle, Tremor, Fall
- **Real-time display** — animated activity ring, confidence bars, top 2 predictions
- **Fall detection alert** — full-screen alert with 10-second countdown, auto-calls 112
- **Activity history** — timestamped log stored locally on your device
- **Activity chart** — visual distribution of all recorded activities
- **Data export** — download history as CSV or JSON
- **Persistent storage** — data survives app close using localStorage (up to 500 records, configurable)
- **Auto-reconnect** — reconnects automatically if BLE signal drops
- **PWA** — installable on Android as a home screen app, works offline

---

## Hardware Required

- Arduino Nano 33 BLE Sense Rev2
- Wrist mount or enclosure (optional)
- Android phone with Chrome browser

---

## Project Structure

```
smartband_ai.html        ← Main app (HTML + CSS + JavaScript, single file)
manifest.json            ← PWA manifest (makes app installable)
sw.js                    ← Service worker (offline support)
nano_ble33_sense_rev2_fusion/
  └── nano_ble33_sense_rev2_fusion.ino   ← Arduino sketch
README.md
```

---

## Arduino Setup

### Libraries Required

Install these in Arduino IDE via **Tools → Manage Libraries**:

| Library | Purpose |
|---|---|
| `ArduinoBLE` | Bluetooth LE communication |
| `Arduino_BMI270_BMM150` | IMU (accelerometer + gyroscope) |
| `Smart_Wristband_Activity_Recognition_inferencing` | Edge Impulse ML model |

> The inferencing library is generated from your Edge Impulse project. Export it as an Arduino library and install via **Sketch → Include Library → Add .ZIP Library**.

### BLE Configuration

| Parameter | Value |
|---|---|
| Device name | `SmartBand` |
| Service UUID | `180C` |
| Characteristic UUID | `2A56` |
| Mode | Notify |

### Data Format

The Arduino sends a UTF-8 string over BLE every inference cycle:

```
PRED:<label1>:<confidence1>:<label2>:<confidence2>
```

Example:
```
PRED:walking:0.921:waving:0.045
```

### Upload Steps

1. Open `nano_ble33_sense_rev2_fusion.ino` in Arduino IDE
2. Select board: **Tools → Board → Arduino Nano 33 BLE**
3. Select the correct COM port
4. Click Upload
5. Open Serial Monitor at 115200 baud to verify output
6. LED solid = BLE connected, LED blinking = error

---

## App Setup & Deployment

### Option 1 — GitHub Pages (Recommended)

Free, permanent HTTPS URL. Web Bluetooth works natively.

1. Create a free account at [github.com](https://github.com)
2. Create a new **public** repository
3. Upload `smartband_ai.html`, `manifest.json`, `sw.js`
4. Go to **Settings → Pages → Source: main branch**
5. Your app is live at `https://yourusername.github.io/repo-name/smartband_ai.html`

### Option 2 — Netlify

1. Rename `smartband_ai.html` to `index.html`
2. Go to [netlify.com](https://netlify.com) and sign up free
3. Drag your project folder onto the deploy area
4. Get an instant URL like `https://your-app.netlify.app`

### Option 3 — html2app.dev (Android APK)

Wraps the app into an installable APK file.

1. Rename `smartband_ai.html` to `index.html`
2. Zip all 3 files together
3. Upload the zip at [html2app.dev](https://html2app.dev)
4. Fill in app name and package name, click Build
5. Download the APK and install on your Android phone

> **Note:** Web Bluetooth may not work inside a basic WebView APK. GitHub Pages + Chrome is more reliable for BLE.

### Installing as a Home Screen App (Android)

1. Open the app URL in **Chrome on Android**
2. Tap the 3-dot menu → **Add to Home Screen**
3. The app installs like a native app with its own icon

---

## Using the App

### Connecting to the Arduino

1. Make sure the Arduino is powered and running the sketch
2. Open the app → tap **Connect to SmartBand**
3. Select `SmartBand` from the Bluetooth device list
4. The status dot turns green — live predictions start appearing

### Tabs

**Home**
- Shows the current activity with emoji, name, and confidence %
- Two prediction cards with animated confidence bars
- Session counter and top activity stats

**History**
- Full timestamped log of all detected activities
- Bar chart showing activity distribution
- Export as CSV or JSON
- Clear history button

**Settings**
- Change the BLE device name to match your Arduino
- Set confidence threshold (predictions below this are not logged)
- Toggle second prediction card
- Toggle fall alert
- Toggle auto-reconnect
- Set max history records
- Export or clear all data

### Demo Mode

In Settings → Simulate Activity, tap any activity button to test the UI without a connected Arduino.

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

> Note: `excercise` is spelled this way intentionally to match the Edge Impulse model label.

---

## Fall Detection

When a fall is detected with confidence above the threshold:

1. A full-screen red alert appears
2. The phone vibrates
3. A 10-second countdown starts
4. Tap **I'm Fine** to dismiss
5. If no response, the app automatically dials **112** (emergency services)

---

## Browser Compatibility

| Browser | BLE Support |
|---|---|
| Chrome on Android | ✅ Full support |
| Chrome on Windows/Mac | ✅ Full support |
| Samsung Internet | ⚠️ Partial |
| Firefox | ❌ Not supported |
| Safari (iOS) | ❌ Not supported |

Web Bluetooth requires **HTTPS**. GitHub Pages and Netlify both provide this automatically.

---

## Data Storage

- All history is stored in `localStorage` on your device
- No data is sent to any server
- Default limit: 500 records (configurable up to 1000)
- When storage is nearly full, the oldest 10% of records are automatically removed
- Export your data as CSV or JSON before clearing

---

## Troubleshooting

**"Web Bluetooth not supported"**
→ Use Chrome on Android or Chrome on desktop. Not Firefox or Safari.

**Device not found during scan**
→ Make sure the Arduino is powered and the sketch is running. Check the device name in Settings matches the Arduino sketch (`SmartBand` by default).

**Connected but no data**
→ Open Arduino Serial Monitor to confirm predictions are printing. Check the BLE service/characteristic UUIDs match between the sketch and the app.

**BLE keeps disconnecting**
→ Enable Auto-Reconnect in Settings. Keep the phone within 5–10 metres of the Arduino.

**Fall alert not triggering**
→ Make sure Fall Alert is enabled in Settings and the confidence threshold is not set too high.

---

## License

MIT License — free to use, modify, and distribute.
