"""
Walks the ACTUAL Street View linked panorama graph (the same graph the
manual arrows in Google Maps use) via browser automation, since this
graph is only exposed through the JavaScript Maps API, not the simple
REST API used elsewhere in this project.

At each step, looks at all panoramas physically linked to the current
one, and moves to whichever link's heading points closest toward the
destination -- walking the real connected path, not just snapping to
the nearest panorama for artificially sampled coordinates.

Setup:
    pip install selenium
    (Selenium 4.6+ auto-manages the Chrome driver, no separate download needed --
    just needs Google Chrome installed on this machine)

    Edit streetview_graph.html and replace YOUR_API_KEY_HERE with your
    real Google Maps API key (must have "Maps JavaScript API" enabled,
    not just Directions/Street View Static).

Usage:
    python streetview_graph_walker.py START_LAT START_LNG END_LAT END_LNG [max_steps]
"""

import json
import math
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def bearing(lat1, lng1, lat2, lng2):
    """Compass bearing (0-360) from point 1 to point 2."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lng2 - lng1)
    x = math.sin(dlambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def heading_difference(a, b):
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


def haversine_meters(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def wait_for_result(driver, timeout=10):
    """Polls window.lastResult until the async JS callback fills it in."""
    start = time.time()
    while time.time() - start < timeout:
        in_progress = driver.execute_script("return window.lookupInProgress;")
        if not in_progress:
            result = driver.execute_script("return window.lastResult;")
            if result is not None:
                return result
        time.sleep(0.2)
    return None


def main():
    if len(sys.argv) < 5:
        print("Usage: python streetview_graph_walker.py START_LAT START_LNG END_LAT END_LNG [max_steps]")
        sys.exit(1)

    start_lat, start_lng = float(sys.argv[1]), float(sys.argv[2])
    end_lat, end_lng = float(sys.argv[3]), float(sys.argv[4])
    max_steps = int(sys.argv[5]) if len(sys.argv) > 5 else 50

    html_path = Path("streetview_graph.html").resolve()
    if not html_path.exists():
        raise FileNotFoundError("streetview_graph.html not found in current directory")

    options = Options()
    options.add_argument("--headless=new")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    driver = webdriver.Chrome(options=options)

    print(f"Loading {html_path}...")
    driver.get(f"file:///{html_path}")

    # Wait for the Google Maps script to actually finish loading, instead
    # of a fixed sleep -- and surface any error if it never does.
    print("Waiting for Google Maps API to load...")
    loaded = False
    for _ in range(20):  # up to ~10 seconds
        is_ready = driver.execute_script(
            "return typeof google !== 'undefined' && typeof google.maps !== 'undefined';"
        )
        if is_ready:
            loaded = True
            break
        time.sleep(0.5)

    if not loaded:
        print("\nGoogle Maps API failed to load. Common causes:")
        print("  1. YOUR_API_KEY_HERE in streetview_graph.html was not replaced with a real key")
        print("  2. The API key doesn't have 'Maps JavaScript API' enabled")
        print("  3. Billing is not enabled on your Google Cloud project")
        print("\nBrowser console log (may show the actual error):")
        for entry in driver.get_log("browser"):
            print(f"  {entry['message']}")
        driver.quit()
        return

    print("Google Maps API loaded successfully.\n")

    print(f"Starting walk from ({start_lat}, {start_lng}) toward ({end_lat}, {end_lng})\n")

    visited = []
    visited_pano_ids = set()

    driver.execute_script(f"lookupPano({start_lat}, {start_lng});")
    result = wait_for_result(driver)

    if not result or not result.get("success"):
        print(f"Failed to find a starting panorama: {result}")
        driver.quit()
        return

    step = 0
    while step < max_steps:
        pano_id = result["pano_id"]
        lat, lng = result["lat"], result["lng"]
        links = result["links"]

        if pano_id in visited_pano_ids:
            print(f"  Step {step}: revisited {pano_id[:12]}... -- stopping (loop detected)")
            break

        visited_pano_ids.add(pano_id)
        visited.append({"step": step, "pano_id": pano_id, "lat": lat, "lng": lng})

        distance_to_goal = haversine_meters(lat, lng, end_lat, end_lng)
        print(f"  Step {step}: {pano_id[:12]}... at ({lat:.5f}, {lng:.5f}) "
              f"-- {distance_to_goal:.0f}m from destination, {len(links)} links available")

        if distance_to_goal < 20:
            print("\nReached destination (within 20m).")
            break

        if not links:
            print("  No further links from this panorama -- dead end, stopping.")
            break

        target_bearing = bearing(lat, lng, end_lat, end_lng)
        best_link = min(links, key=lambda link: heading_difference(link["heading"], target_bearing))

        driver.execute_script(f"lookupPanoById('{best_link['pano']}');")
        result = wait_for_result(driver)

        if not result or not result.get("success"):
            print(f"  Failed to load next panorama: {result}")
            break

        step += 1

    driver.quit()

    output_path = Path("output/linked_pano_chain.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(visited, f, indent=2)

    print(f"\nWalked {len(visited)} connected panoramas.")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()