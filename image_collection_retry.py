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
import time

from image_collection.streetview_fetcher import download_image, has_road_visible

# Try the originally-calculated heading first, then these offsets from it,
# in order, until one shows a clear road.
HEADING_OFFSETS = [0, -30, 30, -60, 60, 180]


def download_image_with_retry(max_retries=3, **kwargs):
    """Wraps download_image with retries for transient network errors."""
    for attempt in range(max_retries):
        try:
            return download_image(**kwargs)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"     Network error ({e}), retrying...")
                time.sleep(2)
            else:
                print(f"     Network error after {max_retries} attempts, skipping this heading")
                return None


def download_pano_chain_with_retries(pano_chain, output_dir="output/images", on_progress=None):
    """Downloads one image per waypoint. Keeps every image that downloads
    successfully -- does NOT filter by road visibility, so nothing gets
    skipped just because the heuristic isn't confident about the road."""
    os.makedirs(output_dir, exist_ok=True)

    for f in os.listdir(output_dir):
        if f.endswith(".jpg") or f.endswith(".png"):
            os.remove(os.path.join(output_dir, f))

    print(f"\nDownloading {len(pano_chain)} images (no skipping)...\n")
    image_paths = []
    failed = 0

    for pano in pano_chain:
        filename = f"step_{pano['step']:04d}_wp{pano['waypoint_index']:04d}.jpg"
        print(f"  Step {pano['step']}/{len(pano_chain)}: {filename}")
        if on_progress:
            on_progress(pano["step"], len(pano_chain))

        filepath = download_image_with_retry(
            pano_id=pano["pano_id"], heading=pano["heading"],
            output_dir=output_dir, filename=filename,
        )
        if not filepath:
            filepath = download_image_with_retry(
                lat=pano["lat"], lng=pano["lng"], heading=pano["heading"],
                output_dir=output_dir, filename=filename,
            )

        if filepath:
            print(f"     Saved: {filename}")
            pano["image"] = filepath
            image_paths.append(pano)
        else:
            print(f"     Download failed (network issue) -- could not save")
            failed += 1

    print(f"\nImages saved  : {len(image_paths)}")
    print(f"Download failures : {failed}")
    return image_paths