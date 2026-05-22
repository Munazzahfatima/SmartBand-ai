"""
SmartBand AI — Edge Impulse ML Model Documentation
====================================================
Project  : Smart Wristband Activity Recognition
Author   : Munazzah
Platform : Edge Impulse → Arduino Nano 33 BLE Sense Rev2
"""

# ─────────────────────────────────────────────────────────────
#  DATASET
# ─────────────────────────────────────────────────────────────

DATASET = {
    "total_duration"  : "1h 55m 14s",
    "training_samples": 645,
    "test_samples"    : 146,
    "total_samples"   : 791,
    "classes": {
        "drinking" : 85,
        "excercise": 80,
        "fall"     : 79,
        "idle"     : 80,
        "tremor"   : 83,
        "walking"  : 85,
        "waving"   : 79,
        "writing"  : 74,
    }
}

# ─────────────────────────────────────────────────────────────
#  IMPULSE DESIGN (Edge Impulse pipeline)
# ─────────────────────────────────────────────────────────────

IMPULSE = {
    "input_block": {
        "type"          : "Time series data",
        "input_axes"    : ["ax", "ay", "az", "gx", "gy", "gz"],
        "window_size_ms": 10000,
        "stride_ms"     : 486.55,
        "frequency_hz"  : 16,
        "zero_pad"      : True,
        "train_subset"  : 100,   # percent
    },
    "processing_block": {
        "type"       : "Spectral Analysis",
        "name"       : "Spectral features",
        "input_axes" : ["ax", "ay", "az", "gx", "gy", "gz"],
        "output"     : "78 spectral features",
    },
    "learning_block": {
        "type"           : "Classification (Keras)",
        "name"           : "Classifier",
        "input_features" : "Spectral features (78)",
        "output_classes" : 8,
    },
    "output_features": [
        "drinking", "excercise", "fall", "idle",
        "tremor", "walking", "waving", "writing"
    ]
}

# ─────────────────────────────────────────────────────────────
#  NEURAL NETWORK ARCHITECTURE
# ─────────────────────────────────────────────────────────────

ARCHITECTURE = {
    "type": "Fully Connected Neural Network (Dense)",
    "layers": [
        {"name": "Input",   "units": 78,  "activation": None},
        {"name": "Dense 1", "units": 128, "activation": "relu"},
        {"name": "Dense 2", "units": 64,  "activation": "relu"},
        {"name": "Dense 3", "units": 32,  "activation": "relu"},
        {"name": "Output",  "units": 8,   "activation": "softmax"},
    ],
    "total_parameters": "~22,000 (estimated)",
}

TRAINING = {
    "epochs"            : 100,
    "optimizer"         : "Learned optimizer (Edge Impulse EON)",
    "training_processor": "CPU",
    "loss_function"     : "Categorical Cross-Entropy",
}

# ─────────────────────────────────────────────────────────────
#  TRAINING RESULTS
# ─────────────────────────────────────────────────────────────

RESULTS = {
    "accuracy"                  : 0.977,   # 97.7%
    "loss"                      : 0.07,
    "area_under_roc_curve"      : 1.00,
    "weighted_avg_precision"    : 0.98,
    "weighted_avg_recall"       : 0.98,
    "weighted_avg_f1_score"     : 0.98,
}

# Per-class results from confusion matrix (validation set)
PER_CLASS_RESULTS = {
    #  class       accuracy   f1_score
    "drinking" : {"accuracy": 0.947, "f1": 0.95},
    "excercise": {"accuracy": 0.944, "f1": 0.97},
    "fall"     : {"accuracy": 1.000, "f1": 1.00},
    "idle"     : {"accuracy": 1.000, "f1": 0.97},
    "tremor"   : {"accuracy": 0.917, "f1": 0.96},
    "walking"  : {"accuracy": 1.000, "f1": 1.00},
    "waving"   : {"accuracy": 1.000, "f1": 0.98},
    "writing"  : {"accuracy": 1.000, "f1": 1.00},
}

# Confusion matrix — rows = actual, cols = predicted
# Order: drinking, excercise, fall, idle, tremor, walking, waving, writing
CONFUSION_MATRIX = [
    [94.7,  0.0,  0.0,  5.3,  0.0,  0.0,  0.0,  0.0],  # drinking
    [ 5.6, 94.4,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],  # excercise
    [ 0.0,  0.0,100.0,  0.0,  0.0,  0.0,  0.0,  0.0],  # fall
    [ 0.0,  0.0,  0.0,100.0,  0.0,  0.0,  0.0,  0.0],  # idle
    [ 0.0,  0.0,  0.0,  0.0, 91.7,  0.0,  8.3,  0.0],  # tremor
    [ 0.0,  0.0,  0.0,  0.0,  0.0,100.0,  0.0,  0.0],  # walking
    [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,100.0,  0.0],  # waving
    [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,100.0],  # writing
]

# ─────────────────────────────────────────────────────────────
#  ON-DEVICE PERFORMANCE (Arduino Nano 33 BLE Sense Rev2)
# ─────────────────────────────────────────────────────────────

ON_DEVICE = {
    "engine"            : "EON Compiler (Edge Optimized Neural)",
    "inferencing_time_ms": 1,
    "peak_ram_kb"       : 1.7,
    "flash_kb"          : 35.0,
    "mcu"               : "nRF52840 (64 MHz Cortex-M4F)",
}

# ─────────────────────────────────────────────────────────────
#  SUMMARY PRINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  SmartBand AI — Model Summary")
    print("=" * 55)

    print(f"\n📦 Dataset")
    print(f"   Total samples  : {DATASET['total_samples']}")
    print(f"   Training        : {DATASET['training_samples']}")
    print(f"   Test            : {DATASET['test_samples']}")
    print(f"   Recording time  : {DATASET['total_duration']}")
    print(f"   Classes         : {len(DATASET['classes'])}")
    for cls, count in DATASET["classes"].items():
        print(f"     {cls:<12} {count} samples")

    print(f"\n🧠 Neural Network")
    print(f"   Type     : {ARCHITECTURE['type']}")
    for layer in ARCHITECTURE["layers"]:
        act = f" ({layer['activation']})" if layer["activation"] else ""
        print(f"   {layer['name']:<10} {layer['units']} units{act}")

    print(f"\n🏋️  Training")
    print(f"   Epochs    : {TRAINING['epochs']}")
    print(f"   Optimizer : {TRAINING['optimizer']}")

    print(f"\n📊 Results (Validation Set)")
    print(f"   Accuracy  : {RESULTS['accuracy']*100:.1f}%")
    print(f"   Loss      : {RESULTS['loss']}")
    print(f"   Precision : {RESULTS['weighted_avg_precision']}")
    print(f"   Recall    : {RESULTS['weighted_avg_recall']}")
    print(f"   F1 Score  : {RESULTS['weighted_avg_f1_score']}")
    print(f"   AUC-ROC   : {RESULTS['area_under_roc_curve']}")

    print(f"\n⚡ On-Device Performance")
    print(f"   Inference : {ON_DEVICE['inferencing_time_ms']} ms")
    print(f"   RAM usage : {ON_DEVICE['peak_ram_kb']} KB")
    print(f"   Flash     : {ON_DEVICE['flash_kb']} KB")
    print(f"   Engine    : {ON_DEVICE['engine']}")
    print("=" * 55)
