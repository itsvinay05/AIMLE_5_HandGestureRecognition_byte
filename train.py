"""
Model Training Script for Hand Gesture Recognition
Trains a CNN classifier on Fist, Left, Palm, and Right hand gestures.
Saves model in Keras format and outputs class_names.json.
"""
import os
import json
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks

# Configuration
IMAGE_SIZE = (128, 128)
BATCH_SIZE = 16
EPOCHS = 15
LEARNING_RATE = 1e-3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VAL_DIR = os.path.join(DATASET_DIR, "val")
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "hand_gesture_model.keras")
CLASS_NAMES_PATH = os.path.join(MODELS_DIR, "class_names.json")

def load_data():
    """Loads training and validation datasets using image_dataset_from_directory."""
    print("Loading training dataset...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        shuffle=True,
        seed=42
    )

    print("Loading validation dataset...")
    val_ds = tf.keras.utils.image_dataset_from_directory(
        VAL_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        shuffle=False
    )

    class_names = train_ds.class_names
    print(f"Classes found ({len(class_names)}): {class_names}")

    # Optimize pipeline with prefetching
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    return train_ds, val_ds, class_names

def build_model(num_classes):
    """Builds a lightweight Convolutional Neural Network suitable for real-time web inference."""
    data_augmentation = tf.keras.Sequential([
        layers.RandomRotation(0.08),
        layers.RandomZoom(0.08),
        layers.RandomTranslation(0.05, 0.05),
    ], name="augmentation")

    model = models.Sequential([
        layers.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3)),
        data_augmentation,
        layers.Rescaling(1.0 / 255.0), # Normalize [0, 255] to [0, 1]

        # Conv Block 1
        layers.Conv2D(32, (3, 3), activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),

        # Conv Block 2
        layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),

        # Conv Block 3
        layers.Conv2D(128, (3, 3), activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),

        # Dense Classifier
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation="softmax")
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model

def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    train_ds, val_ds, class_names = load_data()

    # Save class names mapping
    with open(CLASS_NAMES_PATH, "w") as f:
        json.dump(class_names, f, indent=2)
    print(f"Saved class names mapping to {CLASS_NAMES_PATH}")

    model = build_model(len(class_names))
    model.summary()

    cb_list = [
        callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
        callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-5),
        callbacks.ModelCheckpoint(MODEL_PATH, monitor="val_accuracy", save_best_only=True)
    ]

    print("\nStarting model training...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=cb_list
    )

    # Final save
    model.save(MODEL_PATH)
    print(f"\nModel training finished! Best model saved to: {MODEL_PATH}")

if __name__ == "__main__":
    main()
