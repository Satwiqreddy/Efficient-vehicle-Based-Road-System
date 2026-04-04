import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def fetch_streetview_image(lat, lng, output_dir="output/images", size="640x480"):
    """
    Downloads a Street View image for a given lat/lng.
    Saves to output_dir as lat_lng.jpg
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{lat}_{lng}.jpg"
    filepath = os.path.join(output_dir, filename)

    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"Already exists: {filename}")
        return filepath

    url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        "size": size,
        "location": f"{lat},{lng}",
        "fov": 90,
        "heading": 0,
        "pitch": 0,
        "key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200 and response.headers["Content-Type"].startswith("image"):
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Saved: {filename}")
        return filepath
    else:
        print(f"No image available for {lat},{lng}")
        return None


def fetch_all_images(waypoints_path="output/waypoints.json"):
    """
    Reads waypoints JSON and fetches Street View image for each.
    Returns list of image file paths.
    """
    with open(waypoints_path, "r") as f:
        waypoints = json.load(f)

    image_paths = []
    for wp in waypoints:
        path = fetch_streetview_image(wp["lat"], wp["lng"])
        if path:
            image_paths.append({
                "lat": wp["lat"],
                "lng": wp["lng"],
                "image": path
            })

    # Save image index
    with open("output/images_index.json", "w") as f:
        json.dump(image_paths, f, indent=2)

    print(f"\nTotal images fetched: {len(image_paths)}")
    return image_paths


if __name__ == "__main__":
    fetch_all_images()