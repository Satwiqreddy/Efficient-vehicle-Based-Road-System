# Design Document
## Ground-Clearance-Aware Navigation System

**Project:** ground-clearance-nav  
**Version:** 1.0  
**Date:** 2026-03-25  

---

## 1. System Overview

This system is a software-only navigation pipeline. There is no custom hardware. The "hardware design" component refers to the computational environment, API dependencies, and the physical constraints being modelled (vehicle ground clearance and road obstacle geometry).

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│          (Web Browser — Flask frontend, Folium map)          │
└───────────────────────────┬─────────────────────────────────┘
                            │ Source, Destination, Vehicle Type
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Route Extraction Module                    │
│        Google Maps Directions API + Polyline Parser          │
│             Output: segments.json (lat/lng list)             │
└───────────────────────────┬─────────────────────────────────┘
                            │ Segment coordinates
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Image Collection Module                     │
│         Google Street View Static API per segment            │
│            Output: images/ (segment_id.jpg)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │ Preprocessed road images
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Road Analysis Module                       │
│     YOLOv8 (obstacle detection) + MiDaS (depth estimation)   │
│         Output: detections.json (severity per segment)       │
└───────────────────────────┬─────────────────────────────────┘
                            │ Obstacle severity scores
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Risk Scoring Module                       │
│       Severity × Vehicle Clearance → Risk Level              │
│           Output: risk_map.json (Low / Med / High)           │
└───────────────────────────┬─────────────────────────────────┘
                            │ Weighted risk graph
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Routing Engine Module                      │
│     Modified A* — Cost = Distance + α × Risk_Score           │
│         Output: safe_route.json (ordered segments)           │
└───────────────────────────┬─────────────────────────────────┘
                            │ Safe route + risk overlay data
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Frontend / Visualizer                      │
│        Folium map with green/yellow/red segment overlay      │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Module Design

### 3.1 Route Extraction Module

**Purpose:** Convert user-supplied source and destination into a list of GPS-tagged road segments.

**Design decisions:**
- Uses Google Maps Directions API (walking/driving mode configurable).
- Encoded polyline is decoded using the `polyline` Python library.
- Segment length fixed at 50 m (configurable via `config.py`). Shorter = more API calls; longer = coarser risk map.
- Output is a JSON array so downstream modules are fully decoupled.

**Key classes / functions:**

| Name | Responsibility |
|---|---|
| `get_route(src, dst)` | Calls Maps API, returns encoded polyline |
| `decode_polyline(encoded)` | Returns list of (lat, lng) tuples |
| `extract_segments(points, length_m)` | Splits path into N-metre segments |

**Output contract (`segments.json`):**
```json
[
  {
    "segment_id": "seg_001",
    "start": { "lat": 13.0827, "lng": 80.2707 },
    "end":   { "lat": 13.0831, "lng": 80.2712 },
    "midpoint": { "lat": 13.0829, "lng": 80.2710 }
  }
]
```

---

### 3.2 Image Collection Module

**Purpose:** Fetch and preprocess one Street View image per segment.

**Design decisions:**
- Street View Static API is used (not the JavaScript API) — returns a JPEG directly, no browser required.
- Camera heading is computed from segment bearing so the image faces the direction of travel.
- Preprocessing pipeline: resize → RGB normalisation → CLAHE contrast enhancement → Gaussian denoise.
- Fallback: if API returns a "no imagery" response, a blank placeholder image is saved and the segment is flagged for neutral risk.

**Key classes / functions:**

| Name | Responsibility |
|---|---|
| `fetch_streetview(lat, lng, heading)` | Downloads JPEG from Street View API |
| `preprocess_image(img)` | Applies resize, normalise, denoise |
| `compute_heading(start, end)` | Bearing angle for camera orientation |

**Output contract:** `output/images/seg_001.jpg` per segment.

---

### 3.3 Road Analysis Module

**Purpose:** Detect road obstacles and estimate their relative severity.

**Design decisions:**
- YOLOv8n (nano variant) is used for speed; fine-tuned or zero-shot on pothole/speed-breaker classes.
- For each detected bounding box, MiDaS (MiDaS v2.1 small) estimates relative depth on the cropped region.
- Depth is normalised to a 0–1 scale within the image. An obstacle occupying depth > 0.6 of the scene range is classified as high severity.
- Running YOLO first avoids running MiDaS on the full image, reducing latency.

**Severity scoring logic:**

```
If no obstacle detected          → severity = 0  (Low)
If obstacle detected:
    depth_score = MiDaS normalised depth of bounding box crop
    If depth_score < 0.3         → severity = 1  (Low)
    If 0.3 ≤ depth_score < 0.6   → severity = 2  (Medium)
    If depth_score ≥ 0.6         → severity = 3  (High)
```

**Output contract (`detections.json`):**
```json
[
  {
    "segment_id": "seg_001",
    "obstacle_detected": true,
    "obstacle_type": "pothole",
    "severity": 3,
    "depth_score": 0.72
  }
]
```

---

### 3.4 Risk Scoring Module

**Purpose:** Translate obstacle severity into a route-level risk score, adjusted for vehicle ground clearance.

**Design decisions:**
- Vehicle clearance profiles are stored in `clearance_rules.py` (e.g., hatchback = 165 mm, sedan = 150 mm, SUV = 200 mm).
- Risk thresholds are inversely scaled with clearance: a lower-clearance vehicle has a lower tolerance for the same obstacle severity.
- Risk score is a float in range [0.0, 1.0], used directly as the weight in the A* cost function.

**Clearance × Severity → Risk Score table:**

| Severity | Clearance < 160 mm | 160–200 mm | > 200 mm |
|---|---|---|---|
| Low (1) | 0.2 | 0.1 | 0.05 |
| Medium (2) | 0.6 | 0.4 | 0.2 |
| High (3) | 1.0 | 0.8 | 0.5 |

**Output contract (`risk_map.json`):**
```json
[
  {
    "segment_id": "seg_001",
    "risk_score": 1.0,
    "risk_label": "High"
  }
]
```

---

### 3.5 Routing Engine Module

**Purpose:** Find the optimal route minimising both distance and road risk.

**Algorithm:** Modified A* (A-Star)

**Cost function:**
```
g(n) = cumulative cost from start to node n
h(n) = heuristic: Haversine distance from n to destination
f(n) = g(n) + h(n)

Edge weight = segment_distance_metres + α × risk_score × 1000
```
(Risk score is scaled by 1000 to bring it into the same order of magnitude as distance in metres. α = 0.7 default.)

**Design decisions:**
- Graph is built using `networkx` with segment midpoints as nodes.
- Both safest and fastest routes are computed (α = 0.7 vs α = 0.0) so the frontend can show both.
- If no low-risk path exists, the system returns the least-risk available path with a warning.

**Output contract (`safe_route.json`):**
```json
{
  "route": ["seg_001", "seg_004", "seg_007"],
  "total_distance_m": 1450,
  "total_risk_score": 0.4,
  "risk_label": "Medium"
}
```

---

### 3.6 Frontend Module

**Purpose:** Web interface for user input and result visualisation.

**Stack:** Flask (backend), Folium (map rendering), HTML/CSS (UI)

**Design decisions:**
- Folium generates a self-contained HTML map file with polyline overlays coloured by risk label.
- Colour scheme: green = Low, orange = Medium, red = High.
- User inputs: source address, destination address, vehicle type (dropdown) or manual clearance (mm).
- Output panel shows: recommended route, alternative route, total distance, risk summary.

---

## 4. Data Flow Diagram

```
[User Input]
     │
     ▼
[Maps API] ──────────────────► segments.json
                                     │
                                     ▼
                          [Street View API] ──► images/
                                                   │
                                                   ▼
                                         [YOLO + MiDaS] ──► detections.json
                                                                   │
                                                                   ▼
                                               [Risk Scorer] ──► risk_map.json
                                                                       │
                                                                       ▼
                                                   [A* Router] ──► safe_route.json
                                                                           │
                                                                           ▼
                                                               [Folium Map Renderer]
                                                                           │
                                                                           ▼
                                                                    [User Browser]
```

---

## 5. Technology Stack Summary

| Layer | Technology | 
|---|---|
| Routing data | Google Maps Directions API | 
| Road imagery | Google Street View Static API | 
| Object detection | YOLOv8 (Ultralytics) |
| Depth estimation | MiDaS v2.1 small | 
| Graph & routing | NetworkX + custom A* | 
| Backend | Python 3.10, Flask | 
| Visualisation | Folium | 

---

## 6. Limitations & Design Tradeoffs

| Limitation | Reason | Mitigation |
|---|---|---|
| MiDaS gives relative depth, not metric mm | Monocular cameras cannot recover absolute scale | Use normalised depth index; frame as clearance risk score, not measurement |
| Street View images may be outdated | Google's data is not real-time | Acknowledge as limitation; note crowdsourced data as future scope |
| No real-time updates | Pipeline is pre-computed per query | Clearly scoped as offline risk mapping; real-time is future scope |
| API cost | Google Maps APIs are paid beyond free tier | Use caching; store segment images locally after first fetch |

---

## 7. Commit Checklist (Design Proof for Guide Review)

The following commits must exist in the repository to satisfy the **Design Proof** rubric criterion:

- [ ] `docs/DESIGN.md` — this file
- [ ] `docs/requirements.md` — requirements specification
- [ ] `modules/route_extraction/` — skeleton with function stubs
- [ ] `modules/image_collection/` — skeleton with function stubs
- [ ] `modules/road_analysis/` — skeleton with function stubs
- [ ] `modules/risk_scoring/` — skeleton with function stubs
- [ ] `modules/routing_engine/` — skeleton with function stubs
- [ ] `modules/frontend/` — skeleton with Flask app stub
- [ ] `config.py` — global constants (SEGMENT_LENGTH_M, ALPHA, clearance profiles)
- [ ] `README.md` — project overview with setup instructions
