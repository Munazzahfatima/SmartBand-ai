/*
 * SmartBand AI — Arduino Nano 33 BLE Sense Rev2
 * Activity Recognition + BLE output
 *
 * BLE Service UUID  : 180C  (User Defined)
 * Characteristic UUID: 2A56  (Digital — used for custom string notify)
 *
 * Data format sent over BLE (UTF-8 string, max 100 bytes):
 *   PRED:<label1>:<val1>:<label2>:<val2>
 *   e.g.  PRED:walking:0.921:waving:0.045
 */

#include <Smart_Wristband_Activity_Recognition_inferencing.h>
#include <Arduino_BMI270_BMM150.h>
#include <ArduinoBLE.h>

// ── BLE setup ────────────────────────────────────────────────────────────────
// Using standard short UUIDs — Web Bluetooth expands these automatically
BLEService activityService("FFE0");
BLEStringCharacteristic predCharacteristic(
    "FFE1",
    BLERead | BLENotify,
    100   // max string length
);

static const bool debug_nn = false;

// ── helpers ──────────────────────────────────────────────────────────────────
void blinkLED(int times, int ms = 100) {
    for (int i = 0; i < times; i++) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(ms);
        digitalWrite(LED_BUILTIN, LOW);
        delay(ms);
    }
}

// ── setup ────────────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);

    // IMU
    if (!IMU.begin()) {
        Serial.println("ERR: IMU init failed");
        while (1) { blinkLED(3, 200); delay(500); }
    }
    Serial.println("IMU OK");
    Serial.print("Acc sample rate: "); Serial.print(IMU.accelerationSampleRate()); Serial.println(" Hz");
    Serial.print("Gyro sample rate: "); Serial.print(IMU.gyroscopeSampleRate()); Serial.println(" Hz");

    // BLE
    if (!BLE.begin()) {
        Serial.println("ERR: BLE init failed");
        while (1) { blinkLED(5, 100); delay(500); }
    }

    BLE.setLocalName("SmartBand");
    BLE.setAdvertisedService(activityService);
    activityService.addCharacteristic(predCharacteristic);
    BLE.addService(activityService);

    predCharacteristic.writeValue("READY");
    BLE.advertise();

    Serial.println("BLE advertising as 'SmartBand'");
    Serial.println("Waiting for connection...");
    blinkLED(2, 300);
}

// ── loop ─────────────────────────────────────────────────────────────────────
void loop() {
    BLEDevice central = BLE.central();

    if (central) {
        Serial.print("Connected: "); Serial.println(central.address());
        digitalWrite(LED_BUILTIN, HIGH);   // solid LED = connected

        while (central.connected()) {
            runInference();
        }

        digitalWrite(LED_BUILTIN, LOW);
        Serial.println("Disconnected");
    }
}

// ── inference ────────────────────────────────────────────────────────────────
void runInference() {
    Serial.println("\nSampling...");

    float buffer[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE] = { 0 };

    for (size_t ix = 0; ix < EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE; ix += 6) {
        int64_t next_tick = (int64_t)micros() +
                            ((int64_t)EI_CLASSIFIER_INTERVAL_MS * 1000);

        while (!IMU.accelerationAvailable() || !IMU.gyroscopeAvailable());

        float ax, ay, az, gx, gy, gz;
        IMU.readAcceleration(ax, ay, az);
        IMU.readGyroscope(gx, gy, gz);

        buffer[ix + 0] = ax;
        buffer[ix + 1] = ay;
        buffer[ix + 2] = az;
        buffer[ix + 3] = gx;
        buffer[ix + 4] = gy;
        buffer[ix + 5] = gz;

        int64_t wait_time = next_tick - (int64_t)micros();
        if (wait_time > 0) delayMicroseconds(wait_time);
    }

    signal_t signal;
    int err = numpy::signal_from_buffer(buffer, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
    if (err != 0) {
        Serial.print("ERR: signal_from_buffer ("); Serial.print(err); Serial.println(")");
        return;
    }

    ei_impulse_result_t result = { 0 };
    err = run_classifier(&signal, &result, debug_nn);
    if (err != EI_IMPULSE_OK) {
        Serial.print("ERR: run_classifier ("); Serial.print(err); Serial.println(")");
        return;
    }

    // Print all scores to Serial
    Serial.println("\nPredictions:");
    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        Serial.print("  ");
        Serial.print(result.classification[ix].label);
        Serial.print(": ");
        Serial.println(result.classification[ix].value, 4);
    }

    // Find top 2
    float first_val = 0.0f, second_val = 0.0f;
    int   first_idx = -1,   second_idx = -1;

    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        float v = result.classification[ix].value;
        if (v > first_val) {
            second_val = first_val; second_idx = first_idx;
            first_val  = v;         first_idx  = ix;
        } else if (v > second_val) {
            second_val = v; second_idx = ix;
        }
    }

    // Human-readable Serial summary
    Serial.println("=============================");
    if (first_idx  >= 0) { Serial.print("  #1: "); Serial.print(result.classification[first_idx].label);  Serial.print(" ("); Serial.print(first_val  * 100, 1); Serial.println("%)"); }
    if (second_idx >= 0) { Serial.print("  #2: "); Serial.print(result.classification[second_idx].label); Serial.print(" ("); Serial.print(second_val * 100, 1); Serial.println("%)"); }
    Serial.println("=============================");

    // Build BLE payload  PRED:label1:val1:label2:val2
    if (first_idx >= 0 && second_idx >= 0) {
        String payload = "PRED:";
        payload += result.classification[first_idx].label;
        payload += ":";
        payload += String(first_val, 3);
        payload += ":";
        payload += result.classification[second_idx].label;
        payload += ":";
        payload += String(second_val, 3);

        Serial.println(payload);
        predCharacteristic.writeValue(payload);
    }

#if EI_CLASSIFIER_HAS_ANOMALY == 1
    Serial.print("  anomaly: "); Serial.println(result.anomaly, 3);
#endif
}
