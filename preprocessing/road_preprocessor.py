import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

INPUT_FOLDER  = "output/images"
OUTPUT_FOLDER = "output/preprocessed_images"

# All objects to remove from road
REMOVE_CLASSES = {
    0: "person",        1: "bicycle",      2: "car",
    3: "motorcycle",    4: "airplane",     5: "bus",
    6: "train",         7: "truck",        9: "traffic light",
    11: "stop sign",   12: "parking meter"
}

def inpaint_objects(image, mask):
    """Remove detected objects and fill with road texture."""
    if mask.max() == 0:
        return image
    mask_uint8 = mask.astype(np.uint8) * 255
    kernel = np.ones((20, 20), np.uint8)
    mask_dilated = cv2.dilate(mask_uint8, kernel, iterations=3)
    return cv2.inpaint(image, mask_dilated, inpaintRadius=12, flags=cv2.INPAINT_TELEA)

def extract_road_mask(image):
    """
    Extract road using bottom portion + edge detection.
    Works better for Indian roads with dividers and colored surroundings.
    """
    h, w = image.shape[:2]

    # ── Method 1: Bottom region focus (road is always bottom 50%) ──
    region_mask = np.zeros((h, w), dtype=np.uint8)
    region_mask[int(h * 0.50):, :] = 255  # only bottom half

    # ── Method 2: Road color (gray/asphalt) ──
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray_road  = cv2.inRange(hsv, np.array([0,   0,  20]), np.array([180, 40, 180]))
    light_road = cv2.inRange(hsv, np.array([0,   0, 160]), np.array([180, 25, 255]))
    color_mask = cv2.bitwise_or(gray_road, light_road)

    # ── Method 3: Exclude known non-road colors ──
    green_mask  = cv2.inRange(hsv, np.array([35,  40,  40]), np.array([85,  255, 255]))  # grass/trees
    sky_mask    = cv2.inRange(hsv, np.array([85,  30,  80]), np.array([130, 255, 255]))  # sky/blue
    yellow_mask = cv2.inRange(hsv, np.array([20,  80,  80]), np.array([35,  255, 255]))  # yellow divider
    exclude     = cv2.bitwise_or(cv2.bitwise_or(green_mask, sky_mask), yellow_mask)

    # Combine: road color + bottom region - excluded colors
    road_mask = cv2.bitwise_and(color_mask, region_mask)
    road_mask = cv2.bitwise_and(road_mask, cv2.bitwise_not(exclude))

    # Morphological cleanup
    kernel_close = np.ones((40, 40), np.uint8)
    kernel_open  = np.ones((15, 15), np.uint8)
    road_mask = cv2.morphologyEx(road_mask, cv2.MORPH_CLOSE, kernel_close)
    road_mask = cv2.morphologyEx(road_mask, cv2.MORPH_OPEN,  kernel_open)

    # Keep only largest connected region (main road surface)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(road_mask)
    if num_labels > 1:
        largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        road_mask = (labels == largest).astype(np.uint8) * 255

    return road_mask

def preprocess_all_images():
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

    print("Loading YOLO model...")
    yolo = YOLO("yolov8m-seg.pt")  # medium model = better detection

    image_paths = list(Path(INPUT_FOLDER).glob("*.jpg")) + \
                  list(Path(INPUT_FOLDER).glob("*.png"))

    print(f"Found {len(image_paths)} images to preprocess...")

    for img_path in image_paths:
        print(f"  Processing: {img_path.name}")
        image = cv2.imread(str(img_path))
        if image is None:
            continue

        # ── STEP A: Remove vehicles, humans with YOLO ────────────────
        results = yolo(image, conf=0.35, verbose=False)[0]
        object_mask = np.zeros(image.shape[:2], dtype=np.uint8)

        if results.masks is not None:
            for i, cls_id in enumerate(results.boxes.cls.cpu().numpy()):
                if int(cls_id) in REMOVE_CLASSES:
                    seg_mask = results.masks.data[i].cpu().numpy()
                    seg_mask = cv2.resize(seg_mask, (image.shape[1], image.shape[0]))
                    object_mask = cv2.bitwise_or(
                        object_mask, (seg_mask > 0.5).astype(np.uint8)
                    )

        # Fill removed objects with road texture (COLOR)
        clean_image = inpaint_objects(image, object_mask)

        # ── STEP B: Extract road surface only ────────────────────────
        road_mask = extract_road_mask(clean_image)

        # Road in full COLOR, surroundings = white background
        road_only = clean_image.copy()
        road_only[road_mask == 0] = [255, 255, 255]

        # ── STEP C: Save outputs ──────────────────────────────────────
        base = img_path.stem
        cv2.imwrite(f"{OUTPUT_FOLDER}/{base}_clean.png",     clean_image)
        cv2.imwrite(f"{OUTPUT_FOLDER}/{base}_road_only.png", road_only)

        # Green overlay to visualize road detection
        overlay = clean_image.copy()
        overlay[road_mask > 0] = (
            overlay[road_mask > 0] * 0.6 + np.array([0, 200, 0]) * 0.4
        ).astype(np.uint8)
        cv2.imwrite(f"{OUTPUT_FOLDER}/{base}_overlay.png", overlay)

        print(f"  ✅ Done: {img_path.name}")

    print(f"\n🎉 Done! Check '{OUTPUT_FOLDER}' folder.")