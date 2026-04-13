import cv2
import numpy as np
import os
import json


def extract_road_region(image_path, output_dir="output/road_images"):
    """
    Extracts only the road region from a Street View image.
    Removes sky, trees, buildings on the sides.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(image_path)
    output_path = os.path.join(output_dir, filename)

    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not read: {image_path}")
        return None

    height, width = img.shape[:2]

    # Step 1 — Crop bottom 60% only (road is always in bottom portion)
    road_crop = img[int(height * 0.4):, :]

    # Step 2 — Convert to grayscale and detect edges
    gray = cv2.cvtColor(road_crop, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    # Step 3 — Define trapezoid mask for road area
    h, w = edges.shape
    mask = np.zeros_like(edges)
    polygon = np.array([[
        (int(w * 0.0), h),          # Bottom left
        (int(w * 0.35), int(h * 0.3)),  # Top left
        (int(w * 0.65), int(h * 0.3)),  # Top right
        (int(w * 1.0), h)           # Bottom right
    ]], dtype=np.int32)
    cv2.fillPoly(mask, polygon, 255)

    # Step 4 — Apply mask to cropped image
    masked = cv2.bitwise_and(road_crop, road_crop, mask=mask)

    # Step 5 — Save result
    cv2.imwrite(output_path, masked)
    print(f"Road extracted: {filename}")
    return output_path


def process_all_images(images_index_path="output/images_index.json"):
    """
    Processes all Street View images and extracts road regions.
    """
    with open(images_index_path, "r") as f:
        images = json.load(f)

    road_images = []
    for item in images:
        path = extract_road_region(item["image"])
        if path:
            road_images.append({
                "lat": item["lat"],
                "lng": item["lng"],
                "image": path
            })

    # Save updated index
    with open("output/road_images_index.json", "w") as f:
        json.dump(road_images, f, indent=2)

    print(f"\nRoad extraction complete. {len(road_images)} images processed.")
    return road_images


if __name__ == "__main__":
    process_all_images()