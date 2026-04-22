import os
import json
import math
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# ── HEADING CALCULATION ───────────────────────────────────────────────────
def calculate_heading(lat1, lng1, lat2, lng2):
    dLng = math.radians(lng2 - lng1)
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    x = math.sin(dLng) * math.cos(lat2_r)
    y = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dLng)
    return (math.degrees(math.atan2(x, y)) + 360) % 360

def angle_difference(a, b):
    diff = abs(a - b) % 360
    return diff if diff <= 180 else 360 - diff

# ── GET PANO METADATA ─────────────────────────────────────────────────────
def get_pano_metadata(lat, lng, radius=50):
    """Get Street View panorama metadata including pano_id."""
    url = "https://maps.googleapis.com/maps/api/streetview/metadata"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "source": "outdoor",
        "key": API_KEY
    }
    return requests.get(url, params=params).json()

def get_pano_by_id(pano_id):
    """Get metadata for a specific panorama by pano_id."""
    url = "https://maps.googleapis.com/maps/api/streetview/metadata"
    params = {
        "pano": pano_id,
        "key": API_KEY
    }
    return requests.get(url, params=params).json()

# ── DOWNLOAD IMAGE ────────────────────────────────────────────────────────
def download_image(pano_id=None, lat=None, lng=None,
                   heading=0, output_dir="output/images",
                   filename="image.jpg", size="640x480"):
    """Download Street View image using pano_id (preferred) or lat/lng."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        "size": size,
        "heading": round(heading, 2),
        "pitch": -10,
        "fov": 75,
        "key": API_KEY
    }

    # Use pano_id if available (more accurate)
    if pano_id:
        params["pano"] = pano_id
    else:
        params["location"] = f"{lat},{lng}"
        params["source"] = "outdoor"
        params["radius"] = 50

    response = requests.get(url, params=params)
    if response.status_code == 200 and response.headers["Content-Type"].startswith("image"):
        with open(filepath, "wb") as f:
            f.write(response.content)
        return filepath
    return None

# ── BUILD PANO CHAIN (real Street View navigation) ────────────────────────
def build_pano_chain(waypoints):
    """
    Build a chain of connected panoramas from origin to destination.
    Like clicking forward in Google Street View.
    """
    print("Building panorama chain...")
    pano_chain   = []
    visited_panos = set()

    for i, wp in enumerate(waypoints):
        lat = wp["lat"]
        lng = wp["lng"]

        # Calculate forward heading
        if i < len(waypoints) - 1:
            heading = calculate_heading(lat, lng, waypoints[i+1]["lat"], waypoints[i+1]["lng"])
        else:
            heading = pano_chain[-1]["heading"] if pano_chain else 0

        # Get panorama at this waypoint
        meta = get_pano_metadata(lat, lng, radius=100)
        if meta.get("status") != "OK":
            print(f"  ⚠ No pano at waypoint {i+1} — skipping")
            continue

        pano_id = meta.get("pano_id")
        pano_lat = meta["location"]["lat"]
        pano_lng = meta["location"]["lng"]

        # Skip if we already have this pano (avoid duplicates)
        if pano_id in visited_panos:
            print(f"  ↩ Waypoint {i+1} — same pano as previous, skipping duplicate")
            continue

        visited_panos.add(pano_id)

        pano_chain.append({
            "step":           len(pano_chain) + 1,
            "waypoint_index": i + 1,
            "pano_id":        pano_id,
            "lat":            pano_lat,
            "lng":            pano_lng,
            "heading":        round(heading, 2),
            "origin_lat":     lat,
            "origin_lng":     lng
        })

        print(f"  ✅ Waypoint {i+1}/{len(waypoints)} → pano_id: {pano_id[:10]}... heading: {round(heading)}°")

    print(f"\n📍 Total unique panoramas: {len(pano_chain)}")
    return pano_chain

# ── DOWNLOAD ALL PANO IMAGES ──────────────────────────────────────────────
def download_pano_chain(pano_chain, output_dir="output/images"):
    """Download all images in the pano chain."""
    os.makedirs(output_dir, exist_ok=True)

    # Clear old images
    for f in os.listdir(output_dir):
        if f.endswith(".jpg") or f.endswith(".png"):
            os.remove(os.path.join(output_dir, f))

    print(f"\nDownloading {len(pano_chain)} images...\n")
    image_paths = []

    for pano in pano_chain:
        filename = f"step_{pano['step']:04d}_wp{pano['waypoint_index']:04d}.jpg"
        print(f"  📸 Downloading step {pano['step']}: {filename}")

        filepath = download_image(
            pano_id    = pano["pano_id"],
            heading    = pano["heading"],
            output_dir = output_dir,
            filename   = filename
        )

        if filepath:
            pano["image"] = filepath
            image_paths.append(pano)
            print(f"     ✅ Saved: {filename}")
        else:
            # Fallback: use lat/lng if pano_id fails
            print(f"     ⚠ pano_id failed, trying lat/lng fallback...")
            filepath = download_image(
                lat        = pano["lat"],
                lng        = pano["lng"],
                heading    = pano["heading"],
                output_dir = output_dir,
                filename   = filename
            )
            if filepath:
                pano["image"] = filepath
                image_paths.append(pano)
                print(f"     ✅ Saved via fallback: {filename}")
            else:
                print(f"     ❌ Failed to download step {pano['step']}")

    return image_paths

# ── MAIN FUNCTION ─────────────────────────────────────────────────────────
def fetch_all_images(waypoints_path="output/waypoints.json"):
    """
    Main function — builds pano chain and downloads all forward-facing images.
    Simulates walking/driving from origin to destination in Street View.
    """
    with open(waypoints_path, "r") as f:
        waypoints = json.load(f)

    print(f"Total waypoints: {len(waypoints)}")
    print(f"Simulating Street View navigation from origin to destination...\n")

    # Step 1: Build panorama chain
    pano_chain = build_pano_chain(waypoints)

    # Step 2: Download all images
    image_paths = download_pano_chain(pano_chain)

    # Step 3: Save full index
    with open("output/images_index.json", "w") as f:
        json.dump(image_paths, f, indent=2)

    print(f"\n✅ Total images downloaded : {len(image_paths)}")
    print(f"📁 Saved in               : output/images/")
    print(f"📄 Index saved in         : output/images_index.json")

    return image_paths

if __name__ == "__main__":
    fetch_all_images()