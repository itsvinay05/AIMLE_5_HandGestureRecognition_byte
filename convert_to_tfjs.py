"""
Model Converter: Keras (.keras) -> TensorFlow.js Web Model
Exports model.json and weight shards to web/public/model/ for direct Vercel deployment.
"""
import os
import shutil
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "hand_gesture_model.keras")
OUTPUT_DIR = os.path.join(BASE_DIR, "web", "public", "model")

def convert():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run train.py first.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Loading Keras model from {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH)

    print(f"Exporting model to TensorFlow.js format at {OUTPUT_DIR}...")
    try:
        import tensorflowjs as tfjs
        tfjs.converters.save_keras_model(model, OUTPUT_DIR)
        print("Model successfully converted to TensorFlow.js format!")
    except ImportError:
        print("tensorflowjs package not found. Attempting CLI fallback...")
        os.system(f'tensorflowjs_converter --input_format=keras "{MODEL_PATH}" "{OUTPUT_DIR}"')

    # Copy class_names.json into web model folder too
    class_names_src = os.path.join(BASE_DIR, "models", "class_names.json")
    if os.path.exists(class_names_src):
        shutil.copy(class_names_src, os.path.join(OUTPUT_DIR, "class_names.json"))
        print("Copied class_names.json to web/public/model/")

if __name__ == "__main__":
    convert()
