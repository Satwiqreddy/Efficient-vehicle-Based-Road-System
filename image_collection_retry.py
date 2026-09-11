"""
Improves on streetview_fetcher.py's download_pano_chain by trying
SEVERAL headings per waypoint before giving up -- instead of skipping
immediately when the single calculated forward-heading doesn't show
a clear road. This matters most on short, local routes where closely
spaced waypoints can produce noisy headings (small GPS jogs, turns,
etc.), causing the camera to point at buildings instead of the road.

Usage (from repo root):
    from image_collection_retry import download_pano_chain_with_retries
    from image_collection.streetview_fetcher import build_pano_chain
    import json

    with open("output/waypoints.json") as f:
        waypoints = json.load(f)
    pano_chain = build_pano_chain(waypoints)
    image_paths = download_pano_chain_with_retries(pano_chain)
"""

import os

from image_collection.streetview_fetcher import download_image, has_road_visible

# Try the originally-calculated heading first, then these offsets from it,
# in order, until one shows a clear road.
HEADING_OFFSETS = [0, -30, 30, -60, 60, 180]


def download_pano_chain_with_retries(pano_chain, output_dir="output/images"):
    """Same behavior as download_pano_chain, but tries multiple headings per waypoint."""
    os.makedirs(output_dir, exist_ok=True)

    for f in os.listdir(output_dir):
        if f.endswith(".jpg") or f.endswith(".png"):
            os.remove(os.path.join(output_dir, f))

    print(f"\nDownloading {len(pano_chain)} images (with heading retries)...\n")
    image_paths = []
    skipped = 0

    for pano in pano_chain:
        filename = f"step_{pano['step']:04d}_wp{pano['waypoint_index']:04d}.jpg"
        print(f"  Step {pano['step']}/{len(pano_chain)}: {filename}")

        found_road = False

        for offset in HEADING_OFFSETS:
            heading = (pano["heading"] + offset) % 360

            filepath = download_image(
                pano_id=pano["pano_id"], heading=heading,
                output_dir=output_dir, filename=filename,
            )
            if not filepath:
                filepath = download_image(
                    lat=pano["lat"], lng=pano["lng"], heading=heading,
                    output_dir=output_dir, filename=filename,
                )
            if not filepath:
                continue

            if has_road_visible(filepath):
                print(f"     Saved (heading offset {offset:+}deg): {filename}")
                pano["image"] = filepath
                pano["heading_used"] = heading
                image_paths.append(pano)
                found_road = True
                break
            else:
                os.remove(filepath)

        if not found_road:
            print(f"     No road visible at any tried heading -- skipping")
            skipped += 1

    print(f"\nImages with road  : {len(image_paths)}")
    print(f"Skipped (no road) : {skipped}")
    return image_paths
