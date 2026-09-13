"""
Downloads actual Street View images for every panorama discovered by
streetview_graph_walker.py -- using the REAL, densely-connected chain
instead of coordinate-snapped guesses.

Usage (from repo root, after running streetview_graph_walker.py):
    python download_linked_chain_images.py
"""

import json
import math
from pathlib import Path

from image_collection.streetview_fetcher import download_image


def bearing(lat1, lng1, lat2, lng2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lng2 - lng1)
    x = math.sin(dlambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def main():
    chain_path = Path("output/linked_pano_chain.json")
    if not chain_path.exists():
        raise FileNotFoundError("Run streetview_graph_walker.py first to produce this file.")

    with open(chain_path) as f:
        chain = json.load(f)

    output_dir = Path("output/images_linked")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading images for {len(chain)} real connected panoramas...\n")

    image_index = []
    for i, node in enumerate(chain):
        # Heading toward the NEXT real panorama in the chain, not a guessed
        # coordinate -- this should be more accurate than before.
        if i < len(chain) - 1:
            next_node = chain[i + 1]
            heading = bearing(node["lat"], node["lng"], next_node["lat"], next_node["lng"])
        else:
            heading = bearing(chain[i - 1]["lat"], chain[i - 1]["lng"], node["lat"], node["lng"])

        filename = f"linked_{i:04d}.jpg"
        filepath = download_image(
            pano_id=node["pano_id"], heading=heading,
            output_dir=str(output_dir), filename=filename,
        )

        if filepath:
            print(f"  {i+1}/{len(chain)}: Saved {filename}")
            image_index.append({
                "image": filepath, "lat": node["lat"], "lng": node["lng"],
                "pano_id": node["pano_id"],
            })
        else:
            print(f"  {i+1}/{len(chain)}: Failed to download")

    with open("output/images_index.json", "w") as f:
        json.dump(image_index, f, indent=2)

    print(f"\nDownloaded {len(image_index)} real images.")
    print("Saved to: output/images_index.json (ready for analyze_route_images.py)")


if __name__ == "__main__":
    main()
