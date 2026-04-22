import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

INPUT_FOLDER  = "output/images"
OUTPUT_FOLDER = "output/preprocessed_images"

REMOVE_CLASSES = {
    0: "person", 1: "bicycle", 2: "car", 3: "motorcycle",
    5: "bus", 7: "truck", 9: "traffic light", 11: "stop sign"
}

# ── A: RESIZE WITH PADDING (no stretching) ──────────────────────────────
def resize_with_padding(image, target_size=256):
    h, w = image.shape[:2]
    scale = target_size / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(image, (new_w, new_h))

    # Pad to square
    pad_top    = (target_size - new_h) // 2
    pad_bottom = target_size - new_h - pad_top
    pad_left   = (target_size - new_w) // 2
    pad_right  = target_size - new_w - pad_left

    padded = cv2.copyMakeBorder(
        resized, pad_top, pad_bottom, pad_left, pad_right,
        cv2.BORDER_CONSTANT, value=[0, 0, 0]
    )
    return padded

# ── B: CROP IRRELEVANT REGIONS (sky, buildings) ──────────────────────────
def crop_road_region(image):
    h, w = image.shape[:2]
    # Remove top 35% (sky/buildings), keep bottom 65% (road)
    cropped = image[int(h * 0.35):, :]
    return cropped

# ── C: NORMALIZE PIXEL VALUES ────────────────────────────────────────────
def normalize(image):
    return image / 255.0

# ── D: NOISE REDUCTION ───────────────────────────────────────────────────
def reduce_noise(image):
    # Mild blur only — don't erase road defects
    return cv2.GaussianBlur(image, (3, 3), 0)

# ── E: CONTRAST ENHANCEMENT (CLAHE) ─────────────────────────────────────
def enhance_contrast(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.merge((l, a, b))
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

# ── F: REMOVE OBJECTS (vehicles, humans) ─────────────────────────────────
def remove_objects(image, yolo):
    results = yolo(image, conf=0.35, verbose=False)[0]
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    if results.masks is not None:
        for i, cls_id in enumerate(results.boxes.cls.cpu().numpy()):
            if int(cls_id) in REMOVE_CLASSES:
                seg = results.masks.data[i].cpu().numpy()
                seg = cv2.resize(seg, (image.shape[1], image.shape[0]))
                mask = cv2.bitwise_or(mask, (seg > 0.5).astype(np.uint8))

    if mask.max() == 0:
        return image  # nothing to remove

    mask_uint8 = mask * 255
    kernel = np.ones((20, 20), np.uint8)
    mask_dilated = cv2.dilate(mask_uint8, kernel, iterations=2)
    return cv2.inpaint(image, mask_dilated, inpaintRadius=12, flags=cv2.INPAINT_TELEA)

# ── G: EDGE DETECTION (highlight cracks/defects) ─────────────────────────
def detect_edges(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1=50, threshold2=150)
    return edges

# ── MAIN PIPELINE ─────────────────────────────────────────────────────────
def preprocess_all_images():
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

    print("Loading YOLO model...")
    yolo = YOLO("yolov8n-seg.pt")

    image_paths = list(Path(INPUT_FOLDER).glob("*.jpg")) + \
                  list(Path(INPUT_FOLDER).glob("*.png"))

    print(f"Found {len(image_paths)} images to preprocess...\n")

    for img_path in image_paths:
        print(f"  Processing: {img_path.name}")
        image = cv2.imread(str(img_path))
        if image is None:
            print(f"  ⚠ Could not read {img_path.name}")
            continue

        base = img_path.stem

        # ── Step 1: Remove vehicles and humans ───────────────────────
        clean = remove_objects(image, yolo)
        cv2.imwrite(f"{OUTPUT_FOLDER}/{base}_1_clean.jpg", clean)

        # ── Step 2: Crop sky and buildings (keep road only) ──────────
        cropped = crop_road_region(clean)
        cv2.imwrite(f"{OUTPUT_FOLDER}/{base}_2_cropped.jpg", cropped)

        # ── Step 3: Enhance contrast (highlight cracks/defects) ──────
        contrasted = enhance_contrast(cropped)
        cv2.imwrite(f"{OUTPUT_FOLDER}/{base}_3_contrast.jpg", contrasted)

        # ── Step 4: Noise reduction (mild) ───────────────────────────
        denoised = reduce_noise(contrasted)
        cv2.imwrite(f"{OUTPUT_FOLDER}/{base}_4_denoised.jpg", denoised)

        # ── Step 5: Resize with padding to 256x256 ───────────────────
        resized = resize_with_padding(denoised, target_size=256)
        cv2.imwrite(f"{OUTPUT_FOLDER}/{base}_5_resized.jpg", resized)

        # ── Step 6: Edge detection (road defects) ────────────────────
        edges = detect_edges(resized)
        cv2.imwrite(f"{OUTPUT_FOLDER}/{base}_6_edges.jpg", edges)

        # ── Step 7: Final normalized image (for ML model input) ──────
        final = normalize(resized)
        final_uint8 = (final * 255).astype(np.uint8)
        cv2.imwrite(f"{OUTPUT_FOLDER}/{base}_7_final.jpg", final_uint8)

        print(f"  ✅ Done: {img_path.name}")

    print(f"\n🎉 Preprocessing complete! Check '{OUTPUT_FOLDER}' folder.")

if __name__ == "__main__":
    preprocess_all_images()