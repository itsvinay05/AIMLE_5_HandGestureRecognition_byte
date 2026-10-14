"""
Single-Image Inference Script for Hand Gesture Recognition
Per Phase 6 of the roadmap.
Usage:
    python predict.py --image demo/sample_hand.jpg
"""
import os
import sys
import json
import argparse
import numpy as np
from PIL import Image
import tensorflow as tf

IMAGE_SIZE = (128, 128)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "hand_gesture_model.keras")
CLASS_NAMES_PATH = os.path.join(MODELS_DIR, "class_names.json")

def load_inference_artifacts():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Run train.py first.")
    if not os.path.exists(CLASS_NAMES_PATH):
        raise FileNotFoundError(f"Class names file not found at {CLASS_NAMES_PATH}. Run train.py first.")

    model = tf.keras.models.load_model(MODEL_PATH)
    with open(CLASS_NAMES_PATH, "r") as f:
        class_names = json.load(f)

    return model, class_names

def predict_gesture(image_path, model=None, class_names=None):
    if model is None or class_names is None:
        model, class_names = load_inference_artifacts()

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at: {image_path}")

    # Read image with PIL, convert to RGB
    img = Image.open(image_path).convert("RGB")
    # Resize to expected model size
    img_resized = img.resize(IMAGE_SIZE)
    img_array = np.array(img_resized, dtype=np.float32)

    # Add batch dimension: (1, 128, 128, 3)
    input_tensor = np.expand_dims(img_array, axis=0)

    # Note: Normalization is built into the model's Rescaling layer, or can be passed directly
    predictions = model.predict(input_tensor, verbose=0)[0]
    best_idx = int(np.argmax(predictions))
    best_class = class_names[best_idx]
    confidence = float(predictions[best_idx])

    print("\nPrediction Results:")
    print("-" * 35)
    print(f"Image:       {image_path}")
    print(f"Predicted:   {best_class}")
    print(f"Confidence:  {confidence * 100:.2f}%")
    print("-" * 35)
    print("Class Probabilities:")
    for cls_name, prob in zip(class_names, predictions):
        bar = "█" * int(prob * 20)
        print(f"  {cls_name:<6}: {prob * 100:6.2f}% {bar}")
    print("-" * 35)

    return best_class, confidence

def main():
    parser = argparse.ArgumentParser(description="Predict hand gesture class for a single image.")
    parser.add_argument("--image", type=str, required=True, help="Path to input hand image")
    args = parser.parse_args()

    predict_gesture(args.image)

if __name__ == "__main__":
    main()
