import os
import json
import math
import requests
import cv2
import numpy as np
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def calculate_heading(lat1, lng1, lat2, lng2):
    dLng = math.radians(lng2 - lng1)
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    x = math.sin(dLng) * math.cos(lat2_r)
    y = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dLng)
    heading = math.degrees(math.atan2(x, y))
    return (heading + 360) % 360

def angle_difference(a, b):
    diff = abs(a - b) % 360
    return diff if diff <= 180 else 360 - diff

def get_metadata(lat, lng, radius=50):
    url = "https://maps.googleapis.com/maps/api/streetview/metadata"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "source": "outdoor",
        "key": API_KEY
    }
    return requests.get(url, params=params).json()

def has_road_visible(filepath):
    """
    Check if downloaded image actually shows a road.
    Road should be visible in bottom 50% of image as gray/dark asphalt.
    Returns True if road is detected.
    """
    image = cv2.imread(filepath)
    if image is None:
        return False

    h, w = image.shape[:2]

    # Focus on bottom 50% (where road should be)
    bottom = image[int(h * 0.50):, :]
    hsv    = cv2.cvtColor(bottom, cv2.COLOR_BGR2HSV)

    # Road = low saturation gray tones (asphalt)
    road_mask = cv2.inRange(hsv, np.array([0, 0, 20]), np.array([180, 50, 180]))

    # Calculate % of bottom area that looks like road
    road_percent = (np.sum(road_mask > 0) / road_mask.size) * 100

    print(f"    🛣 Road visibility: {round(road_percent, 1)}%")

    # Need at least 15% road pixels in bottom half
    return road_percent >= 15

def find_forward_facing_location(lat, lng, desired_heading, threshold=30):
    """
    Find best forward-facing Street View near waypoint.
    Stricter threshold (30°) to avoid sideways images.
    """
    search_radii     = [50, 100, 200, 500]
    offset_distances = [0.0001, 0.0002, 0.0005]

    heading_rad = math.radians(desired_heading)
    dlat = math.cos(heading_rad)
    dlng = math.sin(heading_rad)

    candidates = [(lat, lng)]
    for dist in offset_distances:
        candidates.append((lat + dlat * dist, lng + dlng * dist))
        candidates.append((lat - dlat * dist, lng - dlng * dist))

    best_location = None
    best_diff     = 360

    for (clat, clng) in candidates:
        for radius in search_radii:
            meta = get_metadata(clat, clng, radius=radius)
            if meta.get("status") != "OK":
                continue

            actual_heading = meta.get("heading", 0)
            diff = angle_difference(actual_heading, desired_heading)

            print(f"    🔍 ({round(clat,4)},{round(clng,4)}) r={radius}m → diff={round(diff)}°")

            if diff < best_diff:
                best_diff     = diff
                best_location = (
                    meta["location"]["lat"],
                    meta["location"]["lng"],
                    actual_heading
                )

            if diff <= threshold:
                print(f"    ✅ Forward-facing found! diff={round(diff)}°")
                return best_location

    if best_location:
        print(f"    ⚠ Best available: diff={round(best_diff)}°")
        return best_location

    return None

def download_image(lat, lng, heading, output_dir, filename, size="640x480"):
    """Download Street View image."""
    url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        "size": size,
        "location": f"{lat},{lng}",
        "fov": 75,
        "heading": round(heading, 2),
        "pitch": -10,
        "source": "outdoor",
        "radius": 50,
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    filepath = os.path.join(output_dir, filename)
    if response.status_code == 200 and response.headers["Content-Type"].startswith("image"):
        with open(filepath, "wb") as f:
            f.write(response.content)
        return filepath
    return None

def fetch_all_images(waypoints_path="output/waypoints.json"):
    with open(waypoints_path, "r") as f:
        waypoints = json.load(f)

    output_dir = "output/images"
    os.makedirs(output_dir, exist_ok=True)

    # Clear old images
    for f in os.listdir(output_dir):
        if f.endswith(".jpg") or f.endswith(".png"):
            os.remove(os.path.join(output_dir, f))

    print(f"Total waypoints: {len(waypoints)}\n")
    image_paths  = []
    last_heading = 0

    for i, wp in enumerate(waypoints):
        lat = wp["lat"]
        lng = wp["lng"]

        # Calculate desired forward heading
        if i < len(waypoints) - 1:
            next_wp = waypoints[i + 1]
            heading = calculate_heading(lat, lng, next_wp["lat"], next_wp["lng"])
        else:
            heading = last_heading
        last_heading = heading

        print(f"\nWaypoint {i+1}/{len(waypoints)} → desired: {round(heading)}°")

        # Find best forward-facing location
        result = find_forward_facing_location(lat, lng, heading, threshold=30)

        if not result:
            print(f"  ❌ No Street View found for waypoint {i+1}")
            continue

        best_lat, best_lng, best_heading = result
        filename = f"waypoint_{i+1:04d}.jpg"

        # Download image
        filepath = download_image(best_lat, best_lng, heading, output_dir, filename)
        if not filepath:
            print(f"  ❌ Download failed for waypoint {i+1}")
            continue

        # ── Check if road is actually visible in image ────────────────
        if not has_road_visible(filepath):
            print(f"  ❌ No road visible in image — searching further...")
            os.remove(filepath)

            # Try with bigger radius
            result2 = find_forward_facing_location(lat, lng, heading, threshold=45)
            if result2:
                best_lat, best_lng, best_heading = result2
                filepath = download_image(best_lat, best_lng, heading, output_dir, filename)
                if filepath and has_road_visible(filepath):
                    print(f"  ✅ Found road-visible image on retry!")
                else:
                    if filepath:
                        os.remove(filepath)
                    print(f"  ❌ Still no road visible — skipping waypoint {i+1}")
                    continue
            else:
                continue

        print(f"  📸 Saved: {filename} ✅")
        image_paths.append({
            "waypoint_index":  i + 1,
            "original_lat":    lat,
            "original_lng":    lng,
            "image_lat":       best_lat,
            "image_lng":       best_lng,
            "desired_heading": round(heading, 2),
            "actual_heading":  round(best_heading, 2),
            "image":           filepath
        })

    # Save index
    with open("output/images_index.json", "w") as f:
        json.dump(image_paths, f, indent=2)

    print(f"\n✅ Forward-facing images with road: {len(image_paths)}/{len(waypoints)}")
    return image_paths

if __name__ == "__main__":
    fetch_all_images()