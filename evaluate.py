"""
Model Evaluation Script for Hand Gesture Recognition
Evaluates the trained model on held-out test data.
Computes Accuracy, Macro Precision, Macro Recall, Macro F1,
and plots the Confusion Matrix per Phase 5 of the roadmap.
"""
import os
import json
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import shutil

IMAGE_SIZE = (128, 128)
BATCH_SIZE = 16

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
TEST_DIR = os.path.join(DATASET_DIR, "test")
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "hand_gesture_model.keras")
CLASS_NAMES_PATH = os.path.join(MODELS_DIR, "class_names.json")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
WEB_RESULTS_DIR = os.path.join(BASE_DIR, "web", "public", "results")

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(WEB_RESULTS_DIR, exist_ok=True)

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run train.py first.")

    with open(CLASS_NAMES_PATH, "r") as f:
        class_names = json.load(f)

    print(f"Loading trained model from {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH)

    print(f"Loading test data from {TEST_DIR}...")
    test_ds = tf.keras.utils.image_dataset_from_directory(
        TEST_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        shuffle=False
    )

    # Collect true labels and predictions
    y_true = []
    y_pred = []

    for images, labels in test_ds:
        preds = model.predict(images, verbose=0)
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        y_pred.extend(np.argmax(preds, axis=1))

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    total_test = len(y_true)

    # Generate Metrics
    report_dict = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)
    report_text = classification_report(y_true, y_pred, target_names=class_names, zero_division=0)

    accuracy = report_dict["accuracy"]
    macro_precision = report_dict["macro avg"]["precision"]
    macro_recall = report_dict["macro avg"]["recall"]
    macro_f1 = report_dict["macro avg"]["f1-score"]

    # Save Confusion Matrix Plot
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(cmap="Blues", ax=ax, values_format="d")
    plt.title("Confusion Matrix - Hand Gesture Recognition", fontsize=12, fontweight="bold")
    plt.tight_layout()

    cm_path = os.path.join(RESULTS_DIR, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()

    # Also copy to web public folder for Vercel
    shutil.copy(cm_path, os.path.join(WEB_RESULTS_DIR, "confusion_matrix.png"))

    # Write metrics.txt
    metrics_path = os.path.join(RESULTS_DIR, "metrics.txt")
    metrics_content = (
        f"=========================================\n"
        f"HAND GESTURE RECOGNITION - EVALUATION REPORT\n"
        f"=========================================\n"
        f"Test accuracy:              {accuracy:.4f}\n"
        f"Macro precision:            {macro_precision:.4f}\n"
        f"Macro recall:               {macro_recall:.4f}\n"
        f"Macro F1-score:             {macro_f1:.4f}\n"
        f"Number of test images:      {total_test}\n"
        f"Classes evaluated:          {', '.join(class_names)}\n"
        f"-----------------------------------------\n"
        f"Detailed Classification Report:\n"
        f"{report_text}\n"
        f"Confusion Matrix saved to: results/confusion_matrix.png\n"
        f"=========================================\n"
    )

    with open(metrics_path, "w") as f:
        f.write(metrics_content)

    # Also copy metrics.json to web public folder for dynamic UI rendering on Vercel
    metrics_json_path = os.path.join(WEB_RESULTS_DIR, "metrics.json")
    with open(metrics_json_path, "w") as f:
        json.dump({
            "accuracy": round(float(accuracy), 4),
            "macroPrecision": round(float(macro_precision), 4),
            "macroRecall": round(float(macro_recall), 4),
            "macroF1": round(float(macro_f1), 4),
            "testCount": int(total_test),
            "classes": class_names,
            "report": report_dict
        }, f, indent=2)

    print("\n" + metrics_content)
    print(f"Metrics saved to: {metrics_path}")
    print(f"Confusion Matrix saved to: {cm_path}")

if __name__ == "__main__":
    main()
