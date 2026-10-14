"""
Phase 7 Demo Media Generator
Creates a contact sheet of prediction examples from test images with overlaid labels.
Saves to demo/predictions_grid.png and copies to web/public/results/
"""
import os
import json
import random
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tensorflow as tf

IMAGE_SIZE = (128, 128)
GRID_COLS = 4
GRID_ROWS = 2 # 8 sample images total

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "hand_gesture_model.keras")
CLASS_NAMES_PATH = os.path.join(MODELS_DIR, "class_names.json")
TEST_DIR = os.path.join(BASE_DIR, "dataset", "test")
DEMO_DIR = os.path.join(BASE_DIR, "demo")
OUTPUT_GRID_PATH = os.path.join(DEMO_DIR, "predictions_grid.png")
WEB_GRID_PATH = os.path.join(BASE_DIR, "web", "public", "results", "predictions_grid.png")

def main():
    os.makedirs(DEMO_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(WEB_GRID_PATH), exist_ok=True)

    if not os.path.exists(MODEL_PATH) or not os.path.exists(CLASS_NAMES_PATH):
        raise FileNotFoundError("Model or class_names.json missing. Run train.py first.")

    model = tf.keras.models.load_model(MODEL_PATH)
    with open(CLASS_NAMES_PATH, "r") as f:
        class_names = json.load(f)

    # Gather test images
    sample_files = []
    for cls in class_names:
        cls_folder = os.path.join(TEST_DIR, cls)
        if os.path.exists(cls_folder):
            files = [os.path.join(cls_folder, f) for f in os.listdir(cls_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if files:
                # Pick up to 2 from each class
                sample_files.extend(random.sample(files, min(2, len(files))))

    if not sample_files:
        print("No test images found to generate demo grid.")
        return

    # Resize card dimension
    card_w, card_h = 160, 200
    grid_img = Image.new("RGB", (GRID_COLS * card_w, GRID_ROWS * card_h), color=(24, 24, 27))
    draw = ImageDraw.Draw(grid_img)

    for i, file_path in enumerate(sample_files[:GRID_COLS * GRID_ROWS]):
        row = i // GRID_COLS
        col = i % GRID_COLS
        x0 = col * card_w
        y0 = row * card_h

        # True class from folder
        true_class = os.path.basename(os.path.dirname(file_path))

        # Predict
        img = Image.open(file_path).convert("RGB")
        resized = img.resize(IMAGE_SIZE)
        input_tensor = np.expand_dims(np.array(resized, dtype=np.float32), axis=0)
        preds = model.predict(input_tensor, verbose=0)[0]
        pred_idx = int(np.argmax(preds))
        pred_class = class_names[pred_idx]
        conf = float(preds[pred_idx])

        # Paste resized image into grid card
        preview_thumb = img.resize((card_w - 20, 130))
        grid_img.paste(preview_thumb, (x0 + 10, y0 + 10))

        # Determine color for banner
        is_correct = (true_class.lower() == pred_class.lower())
        banner_color = (34, 197, 94) if is_correct else (239, 68, 68)

        # Draw caption
        draw.rectangle([x0 + 10, y0 + 145, x0 + card_w - 10, y0 + 185], fill=(39, 39, 42))
        draw.text((x0 + 15, y0 + 150), f"True: {true_class}", fill=(200, 200, 200))
        draw.text((x0 + 15, y0 + 166), f"Pred: {pred_class} ({int(conf * 100)}%)", fill=banner_color)

    grid_img.save(OUTPUT_GRID_PATH)
    shutil.copy(OUTPUT_GRID_PATH, WEB_GRID_PATH)
    print(f"Generated demonstration contact sheet saved to: {OUTPUT_GRID_PATH}")

if __name__ == "__main__":
    main()
