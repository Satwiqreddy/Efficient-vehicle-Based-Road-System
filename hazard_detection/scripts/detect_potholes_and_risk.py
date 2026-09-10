"""
Complete pothole pipeline, mirroring detect_speedbreakers_and_risk.py.
For every image in --source:

  1. Run the trained YOLO pothole model on it.
  2. If a pothole is found:
       - draw the box on the image
       - estimate severity using DEPTH (comparing the pothole's depth
         against the surrounding road surface) -- richer than the
         box-area heuristic used for speed breakers, since potholes are
         depressions and depth is a meaningful visual signal for them.
       - combine confidence + severity + vehicle ground clearance into
         a personalized risk score and Low/Medium/High class
       - save the annotated image into output/detected/
  3. If nothing is found: save the original image into output/no_pothole/
  4. Write one row per image into results.csv.

Usage (from project root, after training a pothole model):
    python scripts/detect_potholes_and_risk.py \
        --model models/pothole_best.pt \
        --source path/to/images \
        --clearance 16.5 \
        --conf 0.3
"""

import argparse
import csv
import shutil
import sys
from pathlib import Path

import cv2
from PIL import Image
from ultralytics import YOLO

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src import risk_engine  # noqa: E402
from src.depth_severity import DepthEstimator, calculate_depth_score  # noqa: E402
from src.utils import get_device  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to trained pothole_best.pt")
    parser.add_argument("--source", required=True, help="Folder of images to process")
    parser.add_argument("--clearance", type=float, required=True,
                         help="Vehicle ground clearance in cm, e.g. 16.5")
    parser.add_argument("--conf", type=float, default=0.3, help="Detection confidence threshold")
    parser.add_argument("--output", default=None, help="Output folder (default: <source>/results)")
    args = parser.parse_args()

    source = Path(args.source)
    images = sorted(
        list(source.glob("*.jpg")) + list(source.glob("*.jpeg")) + list(source.glob("*.png"))
    )
    if not images:
        raise FileNotFoundError(f"No images found in {source}")

    output_root = Path(args.output) if args.output else source / "results"
    detected_dir = output_root / "detected"
    no_detection_dir = output_root / "no_pothole"
    detected_dir.mkdir(parents=True, exist_ok=True)
    no_detection_dir.mkdir(parents=True, exist_ok=True)

    device = get_device()
    model = YOLO(args.model)
    depth_estimator = DepthEstimator(device)

    rows = []
    detected_count = 0

    for img_path in images:
        cv_image = cv2.imread(str(img_path))
        if cv_image is None:
            continue
        h, w = cv_image.shape[:2]

        result = model.predict(source=str(img_path), conf=args.conf, verbose=False)[0]

        if len(result.boxes) == 0:
            shutil.copy(img_path, no_detection_dir / img_path.name)
            rows.append({
                "image": img_path.name,
                "pothole_detected": False,
                "confidence": "",
                "relative_depth": "",
                "risk_score": "",
                "risk_class": "",
            })
            continue

        # Depth estimation needs the image loaded via PIL, separately from
        # the OpenCV image used for drawing boxes below.
        pil_image = Image.open(img_path).convert("RGB")
        depth_map = depth_estimator.estimate(pil_image)

        best_idx = result.boxes.conf.argmax().item()
        confidence = float(result.boxes.conf[best_idx])
        box = result.boxes.xyxy[best_idx].tolist()

        depth_result = calculate_depth_score(depth_map, box)

        if depth_result is None:
            # Depth estimation failed for this box (degenerate ROI) --
            # fall back to confidence-only severity rather than crashing.
            severity = confidence
            relative_depth = None
        else:
            pothole_depth, road_depth, difference = depth_result
            relative_depth = abs(difference) / (abs(road_depth) + 1e-6)
            severity = min(relative_depth / 0.2, 1.0)  # same normalization as depth_severity.py

        base_risk = risk_engine.combined_risk_score(confidence, severity)
        final_risk = risk_engine.personalized_risk(base_risk, args.clearance)
        risk_class = risk_engine.risk_class(final_risk)

        x1, y1, x2, y2 = map(int, box)
        color = {"Low": (0, 200, 0), "Medium": (0, 165, 255), "High": (0, 0, 255)}[risk_class]
        cv2.rectangle(cv_image, (x1, y1), (x2, y2), color, 3)
        label = f"{risk_class} risk ({final_risk:.2f})"
        cv2.putText(cv_image, label, (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        cv2.imwrite(str(detected_dir / img_path.name), cv_image)
        detected_count += 1

        rows.append({
            "image": img_path.name,
            "pothole_detected": True,
            "confidence": round(confidence, 3),
            "relative_depth": round(relative_depth, 3) if relative_depth is not None else "",
            "risk_score": round(final_risk, 3),
            "risk_class": risk_class,
        })

    csv_path = output_root / "results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "image", "pothole_detected", "confidence", "relative_depth", "risk_score", "risk_class"
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Total images: {len(images)}")
    print(f"Pothole detected: {detected_count} -> {detected_dir}")
    print(f"No pothole: {len(images) - detected_count} -> {no_detection_dir}")
    print(f"Full report: {csv_path}")


if __name__ == "__main__":
    main()
