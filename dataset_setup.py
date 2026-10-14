"""
Dataset Setup & Pure-Python Sample Generator for Hand Gesture Recognition
Prepares train/val/test splits for the 4 classes: Fist, Left, Palm, Right.
Uses pure Python standard library to write standard .bmp images (no PIL required for setup).
"""
import os
import struct
import random

CLASSES = ["Fist", "Left", "Palm", "Right"]
SPLITS = {"train": 40, "val": 10, "test": 10}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

def create_bmp_image(width, height, draw_func):
    """Creates a 24-bit uncompressed BMP image in pure Python (no PIL required)."""
    # BMP row size must be a multiple of 4 bytes
    row_bytes = (width * 3 + 3) & (~3)
    pixel_data_size = row_bytes * height
    file_size = 54 + pixel_data_size

    # BMP Header
    bmp_header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)
    # DIB Header (BITMAPINFOHEADER)
    dib_header = struct.pack('<IIIHHIIIIII', 40, width, height, 1, 24, 0, pixel_data_size, 2835, 2835, 0, 0)

    # Pixel array (bottom-to-top)
    pixels = bytearray(pixel_data_size)
    for y in range(height):
        for x in range(width):
            # Invert y because BMP is bottom-to-top
            r, g, b = draw_func(x, height - 1 - y, width, height)
            idx = y * row_bytes + x * 3
            pixels[idx] = b     # Blue
            pixels[idx + 1] = g # Green
            pixels[idx + 2] = r # Red

    return bmp_header + dib_header + bytes(pixels)

def draw_gesture_pixel(gesture, x, y, width, height):
    cx, cy = width // 2, height // 2
    # Dark modern background
    r_bg, g_bg, b_bg = 24, 24, 32

    # Skin color
    r_skin, g_skin, b_skin = 240, 195, 150

    dx = x - cx
    dy = y - cy
    dist_sq = dx * dx + dy * dy

    if gesture == "Fist":
        # Round clenched fist ball
        if dist_sq < 30 * 30:
            return r_skin, g_skin, b_skin

    elif gesture == "Palm":
        # Palm base circle
        if dist_sq < 22 * 22:
            return r_skin, g_skin, b_skin
        # 5 fingers pointing up
        for off in [-20, -10, 0, 10, 20]:
            if abs(x - (cx + off)) <= 3 and -38 <= dy <= 0:
                return r_skin, g_skin, b_skin

    elif gesture == "Left":
        # Hand body
        if dist_sq < 20 * 20:
            return r_skin, g_skin, b_skin
        # Finger pointing left
        if -38 <= dx <= 0 and abs(dy) <= 4:
            return r_skin, g_skin, b_skin

    elif gesture == "Right":
        # Hand body
        if dist_sq < 20 * 20:
            return r_skin, g_skin, b_skin
        # Finger pointing right
        if 0 <= dx <= 38 and abs(dy) <= 4:
            return r_skin, g_skin, b_skin

    return r_bg, g_bg, b_bg

def ensure_dataset():
    total_created = 0
    for split, count in SPLITS.items():
        for cls in CLASSES:
            folder = os.path.join(DATASET_DIR, split, cls)
            os.makedirs(folder, exist_ok=True)
            existing = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            if len(existing) == 0:
                print(f"Creating {count} starter samples for {split}/{cls}...")
                for i in range(count):
                    bmp_bytes = create_bmp_image(
                        128, 128,
                        lambda x, y, w, h: draw_gesture_pixel(cls, x, y, w, h)
                    )
                    file_path = os.path.join(folder, f"{cls.lower()}_{i:03d}.bmp")
                    with open(file_path, "wb") as f:
                        f.write(bmp_bytes)
                    total_created += 1

    # Also create demo sample in demo/
    demo_dir = os.path.join(BASE_DIR, "demo")
    os.makedirs(demo_dir, exist_ok=True)
    sample_demo = os.path.join(demo_dir, "sample_hand.bmp")
    if not os.path.exists(sample_demo):
        with open(sample_demo, "wb") as f:
            f.write(create_bmp_image(128, 128, lambda x, y, w, h: draw_gesture_pixel("Palm", x, y, w, h)))

    if total_created > 0:
        print(f"Dataset successfully initialized with {total_created} sample images.")
    else:
        print("Existing dataset found in dataset/ directories.")

if __name__ == "__main__":
    ensure_dataset()
